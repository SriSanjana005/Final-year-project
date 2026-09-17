import sys
import os
import logging

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.models.child import ChildProfile
from app.models.recommendation import Recommendation
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz import Quiz
from app.services.ai_availability_service import AIAvailabilityService
from app.services.content_selection_service import ContentSelectionService
from app.services.transformer_service import TransformerService
from ml.reinforcement_learning.actions import ActionType
from ml.reinforcement_learning.policy import LearnerStateAdapter
from stable_baselines3 import PPO

logger = logging.getLogger(__name__)

PPO_CHECKPOINT_PATH = os.path.join(PROJECT_ROOT, "ml", "models", "ppo_recommendation_agent.zip")
_ppo_model_cache = None

def load_ppo_agent():
    global _ppo_model_cache
    if _ppo_model_cache is None and os.path.exists(PPO_CHECKPOINT_PATH):
        try:
            _ppo_model_cache = PPO.load(PPO_CHECKPOINT_PATH)
            logger.info(f"Loaded PPO agent checkpoint successfully from {PPO_CHECKPOINT_PATH}")
        except Exception as e:
            logger.error(f"Failed to load PPO model checkpoint: {e}")
            _ppo_model_cache = None
    return _ppo_model_cache

class AIRecommendationService:
    @staticmethod
    def generate_personalized_recommendation(db: Session, child_id: int) -> Optional[Recommendation]:
        """
        Orchestrates end-to-end recommendation flow:
        Checks AI availability & Strategy config -> Transformer inference -> 68-D PPO action -> 
        Content Selection -> Returns Recommendation record. Safe fallback to rule-based baseline.
        """
        logger.info(f"Initiating recommendation request for child #{child_id}")

        # 1. Check AI availability & strategy selection matrix
        status_matrix = AIAvailabilityService.check_ai_status(db, child_id)
        strategy = status_matrix["strategy_selected"]
        logger.info(f"Child #{child_id} strategy evaluation: selected='{strategy}', reason='{status_matrix['reason']}'")

        # 2. If strategy evaluates to rule_based (cold-start, missing models, or configured strategy), fallback cleanly
        if strategy == "rule_based":
            from app.services.recommendation_service import RecommendationService
            logger.info(f"Delegating recommendation generation for child #{child_id} to RuleBasedRecommendationStrategy.")
            return RecommendationService.generate_rule_based_recommendation(db, child_id)

        # 3. TRANSFORMER + PPO INFERENCE PIPELINE
        try:
            # A. Extract Transformer Learner State (64-D Vector)
            learner_state_info = TransformerService.get_learner_state(db, child_id)
            if learner_state_info.get("model_status") != "available":
                logger.warning(f"Transformer state unavailable for child #{child_id}; falling back to rule-based.")
                from app.services.recommendation_service import RecommendationService
                return RecommendationService.generate_rule_based_recommendation(db, child_id)

            vec_summary = learner_state_info.get("vector_summary", {})
            vector_mean = vec_summary.get("mean", 0.0)

            # B. Retrieve recent performance context for 68-D PPO vector construction
            recent_attempts = (
                db.query(QuizAttempt)
                .filter(QuizAttempt.child_id == child_id)
                .order_by(desc(QuizAttempt.completed_at))
                .limit(5)
                .all()
            )
            
            recent_avg_score = 0.75
            latest_topic_id = None
            current_difficulty = "easy"

            if recent_attempts:
                scores = [a.percentage / 100.0 for a in recent_attempts]
                recent_avg_score = sum(scores) / len(scores)
                latest_quiz = db.query(Quiz).filter(Quiz.id == recent_attempts[0].quiz_id).first()
                if latest_quiz:
                    latest_topic_id = latest_quiz.topic_id
                    current_difficulty = latest_quiz.difficulty or "easy"

            completion_rate = min(1.0, len(recent_attempts) / 5.0)
            recent_time_spent = 0.5  # Normalized time metric

            learner_state_vector = learner_state_info.get("learner_state_vector") or [0.1] * 64

            # C. Construct 68-D RL State Vector
            adapter = LearnerStateAdapter()
            obs_vector = adapter.build_observation_vector(
                transformer_representation=learner_state_vector,
                recent_avg_score=recent_avg_score,
                completion_rate=completion_rate,
                recent_time_spent=recent_time_spent,
                current_difficulty_str=current_difficulty
            )

            # D. Execute PPO Policy Agent Inference
            ppo_agent = load_ppo_agent()
            if not ppo_agent:
                logger.warning("PPO model agent instance unavailable during execution; falling back to rule-based.")
                from app.services.recommendation_service import RecommendationService
                return RecommendationService.generate_rule_based_recommendation(db, child_id)

            action_idx, _ = ppo_agent.predict(obs_vector, deterministic=True)
            action_type = ActionType(int(action_idx))
            logger.info(f"PPO Agent selected action {action_type.name} (code={action_type.value}) for child #{child_id}")

            # E. Map Action to Published Admin Content via ContentSelectionService
            selected_content = ContentSelectionService.select_content_for_action(
                db=db,
                child_id=child_id,
                action_type=action_type,
                current_topic_id=latest_topic_id,
                current_difficulty=current_difficulty
            )

            if not selected_content:
                logger.warning(f"Content selection returned None for action {action_type.name}; falling back to rule-based.")
                from app.services.recommendation_service import RecommendationService
                return RecommendationService.generate_rule_based_recommendation(db, child_id)

            # F. Construct Child-Friendly Non-Diagnostic Reason
            friendly_reasons = {
                ActionType.REVIEW_PREVIOUS_TOPIC: "Here is a quick review activity to help reinforce what you learned.",
                ActionType.EASIER_CONTENT: "Recommended based on your recent learning activity to build confidence.",
                ActionType.SAME_DIFFICULTY: "This activity matches your recent learning progress and difficulty level.",
                ActionType.HARDER_CONTENT: "You're doing great! Here is a slightly more challenging activity for you.",
                ActionType.PRACTICE_CONTENT: "You may be ready for a little extra hands-on practice activity!"
            }
            reason = friendly_reasons.get(action_type, "Recommended based on your recent learning activity.")

            # G. Persist Recommendation Record with type 'transformer_ppo'
            rec = Recommendation(
                child_id=child_id,
                content_id=selected_content.id,
                topic_id=selected_content.topic_id,
                target_difficulty=selected_content.difficulty or current_difficulty,
                reason=reason,
                recommendation_type="transformer_ppo",
                status="recommended",
                avg_score=round(recent_avg_score * 100.0, 1)
            )
            db.add(rec)
            db.commit()
            db.refresh(rec)
            logger.info(f"Successfully created PPO recommendation #{rec.id} (content #{selected_content.id}) for child #{child_id}")
            return rec

        except Exception as e:
            logger.error(f"Unexpected error in AI recommendation inference pipeline: {e}", exc_info=True)
            from app.services.recommendation_service import RecommendationService
            return RecommendationService.generate_rule_based_recommendation(db, child_id)
