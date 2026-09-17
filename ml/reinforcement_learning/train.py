import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from stable_baselines3 import PPO
from ml.config.training_config import config
from ml.reinforcement_learning.environment import LearnerRecommendationEnv

def train_ppo_agent(
    total_timesteps: int = config.PPO_TOTAL_TIMESTEPS,
    learning_rate: float = config.PPO_LEARNING_RATE
) -> Dict[str, Any]:
    """
    Trains Stable-Baselines3 PPO Policy Agent using Gymnasium LearnerRecommendationEnv.
    Saves PPO model checkpoint zip and metadata JSON.
    """
    os.makedirs(config.PPO_MODEL_DIR, exist_ok=True)
    os.makedirs(os.path.join(PROJECT_ROOT, "ml", "models"), exist_ok=True)

    checkpoint_path = os.path.join(config.PPO_MODEL_DIR, "ppo_recommendation_agent.zip")
    root_checkpoint_path = os.path.join(PROJECT_ROOT, "ml", "models", "ppo_recommendation_agent.zip")

    env = LearnerRecommendationEnv()

    model = PPO(
        policy="MlpPolicy",
        env=env,
        learning_rate=learning_rate,
        n_steps=config.PPO_N_STEPS,
        batch_size=config.PPO_BATCH_SIZE,
        n_epochs=4,
        gamma=config.PPO_GAMMA,
        gae_lambda=config.PPO_GAE_LAMBDA,
        clip_range=config.PPO_CLIP_RANGE,
        ent_coef=config.PPO_ENT_COEF,
        seed=config.PPO_SEED,
        verbose=1
    )

    print(f"Starting PPO training for {total_timesteps} timesteps...")
    model.learn(total_timesteps=total_timesteps)

    # Save checkpoints to both PPO_MODEL_DIR and root models directory for backward compatibility
    model.save(checkpoint_path)
    model.save(root_checkpoint_path)

    metadata = {
        "training_status": "trained",
        "timestamp": datetime.utcnow().isoformat(),
        "total_timesteps": total_timesteps,
        "learning_rate": learning_rate,
        "environment_type": "LearnerRecommendationEnv (Gymnasium)",
        "environment_label": "DEVELOPMENT-ONLY — NOT FOR FYP EVALUATION (Replay/observational historical data environment)",
        "state_dimension": 68,
        "action_dimension": 5,
        "checkpoint_path": checkpoint_path
    }

    meta_path = os.path.join(config.PPO_MODEL_DIR, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Successfully saved PPO agent checkpoint to {checkpoint_path}")
    return metadata

if __name__ == "__main__":
    train_ppo_agent()
