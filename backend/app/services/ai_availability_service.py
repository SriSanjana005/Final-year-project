import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.config import settings
from app.models.learning_history import LearningHistory
from app.models.quiz_attempt import QuizAttempt
from app.services.transformer_service import TransformerService
from stable_baselines3 import PPO

PPO_CHECKPOINT_PATH = os.path.join(PROJECT_ROOT, "ml", "models", "ppo_recommendation_agent.zip")

class AIAvailabilityService:
    @staticmethod
    def is_ppo_model_available() -> bool:
        """Verifies PPO agent checkpoint exists and is loadable."""
        if not os.path.exists(PPO_CHECKPOINT_PATH):
            return False
        try:
            # Quick validation that PPO can be loaded
            _ = PPO.load(PPO_CHECKPOINT_PATH)
            return True
        except Exception as e:
            print(f"Notice: PPO checkpoint validation failed: {e}")
            return False

    @staticmethod
    def is_transformer_model_available() -> bool:
        """Verifies Transformer learner state extractor pipeline is functional."""
        try:
            from ml.transformer.inference import LearnerStateExtractor
            extractor = LearnerStateExtractor()
            return extractor is not None
        except Exception as e:
            print(f"Notice: Transformer extractor validation failed: {e}")
            return False

    @staticmethod
    def get_learner_interaction_count(db: Session, child_id: int) -> int:
        """Returns total count of completed learning interactions for learner."""
        histories_count = db.query(LearningHistory).filter(LearningHistory.child_id == child_id).count()
        quiz_attempts_count = db.query(QuizAttempt).filter(QuizAttempt.child_id == child_id).count()
        return max(histories_count, quiz_attempts_count)

    @staticmethod
    def check_ai_status(db: Session, child_id: int) -> Dict[str, Any]:
        """
        Evaluates full AI availability matrix for a learner.
        """
        t_avail = AIAvailabilityService.is_transformer_model_available()
        ppo_avail = AIAvailabilityService.is_ppo_model_available()
        
        interaction_count = AIAvailabilityService.get_learner_interaction_count(db, child_id)
        cold_start = interaction_count < settings.MIN_INTERACTIONS_FOR_AI

        # Verify if Transformer can extract valid state representation for child
        learner_state_avail = False
        if not cold_start and t_avail:
            l_state = TransformerService.get_learner_state(db, child_id)
            learner_state_avail = l_state.get("model_status") == "available"

        # Determine strategy selection based on global config and availability
        global_strategy = settings.RECOMMENDATION_STRATEGY.upper()
        
        if global_strategy == "RULE_BASED":
            selected_strategy = "rule_based"
            reason = "Configured strategy is explicitly RULE_BASED."
        elif global_strategy == "TRANSFORMER_PPO":
            if t_avail and ppo_avail and learner_state_avail:
                selected_strategy = "transformer_ppo"
                reason = "Explicit TRANSFORMER_PPO strategy active with verified AI models."
            else:
                selected_strategy = "rule_based"
                reason = "TRANSFORMER_PPO requested but models or learner state unavailable. Failing safely to rule_based."
        else:  # AUTO (default)
            if t_avail and ppo_avail and learner_state_avail and not cold_start:
                selected_strategy = "transformer_ppo"
                reason = "AUTO strategy selected Transformer+PPO for learner with sufficient history."
            else:
                selected_strategy = "rule_based"
                reason = f"AUTO strategy using rule_based (cold_start={cold_start}, interaction_count={interaction_count})."

        return {
            "transformer_available": t_avail,
            "ppo_available": ppo_avail,
            "learner_state_available": learner_state_avail,
            "cold_start": cold_start,
            "interaction_count": interaction_count,
            "min_required_interactions": settings.MIN_INTERACTIONS_FOR_AI,
            "global_configured_strategy": global_strategy,
            "strategy_selected": selected_strategy,
            "reason": reason
        }
