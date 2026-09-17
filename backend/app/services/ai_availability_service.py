import sys
import os
import json

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
PPO_META_PATH = os.path.join(PROJECT_ROOT, "ml", "models", "ppo", "metadata.json")
PPO_EVAL_PATH = os.path.join(PROJECT_ROOT, "ml", "models", "ppo", "ppo_evaluation_results.json")

TRANSFORMER_CHECKPOINT_PATH = os.path.join(PROJECT_ROOT, "ml", "models", "transformer", "best_transformer.pt")
TRANSFORMER_META_PATH = os.path.join(PROJECT_ROOT, "ml", "models", "transformer", "metadata.json")
TRANSFORMER_EVAL_PATH = os.path.join(PROJECT_ROOT, "ml", "models", "transformer", "evaluation_results.json")

class AIAvailabilityService:
    @staticmethod
    def get_transformer_status() -> Dict[str, Any]:
        """Returns truthful Transformer training, initialization, and evaluation status."""
        is_instantiated = False
        try:
            from ml.transformer.inference import LearnerStateExtractor
            extractor = LearnerStateExtractor()
            is_instantiated = extractor is not None
        except Exception:
            is_instantiated = False

        checkpoint_exists = os.path.exists(TRANSFORMER_CHECKPOINT_PATH)
        
        meta = {}
        if os.path.exists(TRANSFORMER_META_PATH):
            try:
                with open(TRANSFORMER_META_PATH, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                meta = {}

        eval_data = {}
        if os.path.exists(TRANSFORMER_EVAL_PATH):
            try:
                with open(TRANSFORMER_EVAL_PATH, "r", encoding="utf-8") as f:
                    eval_data = json.load(f)
            except Exception:
                eval_data = {}

        if checkpoint_exists and meta.get("training_status") == "trained":
            status_str = "trained"
        elif is_instantiated:
            status_str = "initialized"
        else:
            status_str = "unavailable"

        metrics = eval_data.get("metrics", {})

        return {
            "status": status_str,
            "available": is_instantiated or checkpoint_exists,
            "checkpoint_exists": checkpoint_exists,
            "trained_timestamp": meta.get("timestamp"),
            "train_samples": meta.get("train_samples", 0),
            "test_accuracy": metrics.get("accuracy", "N/A — insufficient data"),
            "test_f1": metrics.get("macro_f1", "N/A — insufficient data"),
            "class_counts": meta.get("class_counts", {})
        }

    @staticmethod
    def get_ppo_status() -> Dict[str, Any]:
        """Returns truthful PPO training and evaluation status."""
        checkpoint_exists = os.path.exists(PPO_CHECKPOINT_PATH) or os.path.exists(
            os.path.join(PROJECT_ROOT, "ml", "models", "ppo", "ppo_recommendation_agent.zip")
        )
        
        is_loadable = False
        if checkpoint_exists:
            try:
                _ = PPO.load(PPO_CHECKPOINT_PATH if os.path.exists(PPO_CHECKPOINT_PATH) else os.path.join(PROJECT_ROOT, "ml", "models", "ppo", "ppo_recommendation_agent.zip"))
                is_loadable = True
            except Exception:
                is_loadable = False

        meta = {}
        if os.path.exists(PPO_META_PATH):
            try:
                with open(PPO_META_PATH, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                meta = {}

        eval_data = {}
        if os.path.exists(PPO_EVAL_PATH):
            try:
                with open(PPO_EVAL_PATH, "r", encoding="utf-8") as f:
                    eval_data = json.load(f)
            except Exception:
                eval_data = {}

        if is_loadable and meta.get("training_status") == "trained":
            status_str = "trained"
        elif is_loadable:
            status_str = "initialized"
        else:
            status_str = "unavailable"

        return {
            "status": status_str,
            "available": is_loadable,
            "checkpoint_exists": checkpoint_exists,
            "trained_timestamp": meta.get("timestamp"),
            "total_timesteps": meta.get("total_timesteps", 0),
            "mean_reward": eval_data.get("mean_episode_reward", "N/A — insufficient data"),
            "environment_label": meta.get("environment_label", "LearnerRecommendationEnv (Gymnasium)")
        }

    @staticmethod
    def get_learner_interaction_count(db: Session, child_id: int) -> int:
        """Returns total count of completed learning interactions for learner."""
        histories_count = db.query(LearningHistory).filter(LearningHistory.child_id == child_id).count()
        quiz_attempts_count = db.query(QuizAttempt).filter(QuizAttempt.child_id == child_id).count()
        return max(histories_count, quiz_attempts_count)

    @staticmethod
    def check_ai_status(db: Session, child_id: int) -> Dict[str, Any]:
        """Evaluates full AI availability matrix for a learner."""
        t_status = AIAvailabilityService.get_transformer_status()
        ppo_status = AIAvailabilityService.get_ppo_status()

        t_avail = t_status["available"]
        ppo_avail = ppo_status["available"]

        interaction_count = AIAvailabilityService.get_learner_interaction_count(db, child_id)
        cold_start = interaction_count < settings.MIN_INTERACTIONS_FOR_AI

        learner_state_avail = False
        if not cold_start and t_avail:
            l_state = TransformerService.get_learner_state(db, child_id)
            learner_state_avail = l_state.get("model_status") == "available"

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
            "transformer_details": t_status,
            "ppo_available": ppo_avail,
            "ppo_details": ppo_status,
            "learner_state_available": learner_state_avail,
            "cold_start": cold_start,
            "interaction_count": interaction_count,
            "min_required_interactions": settings.MIN_INTERACTIONS_FOR_AI,
            "global_configured_strategy": global_strategy,
            "strategy_selected": selected_strategy,
            "reason": reason
        }
