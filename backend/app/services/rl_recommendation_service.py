import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.models.child import ChildProfile
from app.models.content import LearningContent
from app.models.topic import Topic
from app.models.learning_history import LearningHistory
from app.models.recommendation import Recommendation
from app.services.transformer_service import TransformerService
from ml.reinforcement_learning.actions import ActionType, get_action_description
from ml.reinforcement_learning.policy import LearnerStateAdapter
from stable_baselines3 import PPO

PPO_CHECKPOINT_PATH = os.path.join(PROJECT_ROOT, "ml", "models", "ppo_recommendation_agent.zip")

_ppo_model_instance = None

def get_ppo_model():
    global _ppo_model_instance
    if _ppo_model_instance is None and os.path.exists(PPO_CHECKPOINT_PATH):
        try:
            _ppo_model_instance = PPO.load(PPO_CHECKPOINT_PATH)
            print(f"Loaded PPO agent checkpoint from {PPO_CHECKPOINT_PATH}")
        except Exception as e:
            print(f"Notice: Failed to load PPO checkpoint: {e}")
            _ppo_model_instance = None
    return _ppo_model_instance

class RLRecommendationService:
    @staticmethod
    def generate_ppo_recommendation(db: Session, child_id: int) -> Optional[Recommendation]:
        """
        Executes Transformer state extraction -> PPO action selection -> Approved Content Mapping.
        Returns Recommendation object with type 'transformer_ppo', or None if fallback is needed.
        """
        # 1. Obtain Transformer Learner State
        learner_state_info = TransformerService.get_learner_state(db, child_id)
        if learner_state_info.get("model_status") != "available":
            # Cold-start or error -> Fallback to Rule-Based Baseline
            return None

        # 2. Load PPO Model Checkpoint
        ppo_model = get_ppo_model()
        if ppo_model is None:
            return None

        # 3. Build 68-D RL State Vector
        adapter = LearnerStateAdapter()
        obs_vector = adapter.build_observation_vector(
            transformer_representation=learner_state_info.get("vector_summary", {}).get("mean", 0.0),
            recent_avg_score=0.75,
            completion_rate=0.8,
            recent_time_spent=0.5,
            current_difficulty_str="easy"
        )

        # 4. Predict PPO Discrete Action
        action_idx, _ = ppo_model.predict(obs_vector, deterministic=True)
        action_type = ActionType(int(action_idx))

        # 5. Translate Action into Content Selection Criteria
        target_difficulty = "easy"
        target_content_type = None
        reason = f"PPO Agent selected {action_type.name}: {get_action_description(int(action_type))}"

        if action_type == ActionType.EASIER_CONTENT:
            target_difficulty = "easy"
        elif action_type == ActionType.SAME_DIFFICULTY:
            target_difficulty = "easy"
        elif action_type == ActionType.HARDER_CONTENT:
            target_difficulty = "medium"
        elif action_type == ActionType.REVIEW_PREVIOUS_TOPIC:
            target_difficulty = "easy"
        elif action_type == ActionType.PRACTICE_CONTENT:
            target_content_type = "practice"

        # 6. Select published admin-approved content matching action criteria
        query = db.query(LearningContent).filter(LearningContent.is_published == True)
        if target_content_type:
            query = query.filter(LearningContent.content_type == target_content_type)
        else:
            query = query.filter(LearningContent.difficulty == target_difficulty)

        candidates = query.all()
        if not candidates:
            candidates = db.query(LearningContent).filter(LearningContent.is_published == True).all()

        if not candidates:
            return None

        # Avoid recently completed repetitions
        histories = db.query(LearningHistory).filter(LearningHistory.child_id == child_id).all()
        completed_ids = {h.activity_id for h in histories}
        uncompleted = [c for c in candidates if c.id not in completed_ids]

        selected_content = uncompleted[0] if uncompleted else candidates[0]

        # 7. Store Recommendation record with type 'transformer_ppo'
        rec = Recommendation(
            child_id=child_id,
            content_id=selected_content.id,
            topic_id=selected_content.topic_id,
            target_difficulty=selected_content.difficulty or target_difficulty,
            reason=reason,
            recommendation_type="transformer_ppo",
            status="recommended",
            avg_score=75.0
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)

        return rec
