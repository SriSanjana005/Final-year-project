import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import torch
from typing import Dict, Any, Optional
from stable_baselines3 import PPO
from ml.reinforcement_learning.environment import LearnerRecommendationEnv


MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ml", "models")
PPO_CHECKPOINT_PATH = os.path.join(MODEL_DIR, "ppo_recommendation_agent.zip")

def train_ppo_agent(
    total_timesteps: int = 1000,
    learning_rate: float = 3e-4,
    save_path: Optional[str] = PPO_CHECKPOINT_PATH
) -> Dict[str, Any]:
    """
    Trains PPO agent in the development recommendation environment and saves checkpoint zip.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)
    env = LearnerRecommendationEnv()

    model = PPO(
        policy="MlpPolicy",
        env=env,
        learning_rate=learning_rate,
        n_steps=64,
        batch_size=16,
        n_epochs=4,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        verbose=1
    )

    print(f"Starting PPO training for {total_timesteps} timesteps...")
    model.learn(total_timesteps=total_timesteps)

    model.save(save_path)
    print(f"Successfully saved PPO agent checkpoint to {save_path}")

    return {
        "status": "success",
        "checkpoint_path": save_path,
        "total_timesteps": total_timesteps,
        "learning_rate": learning_rate
    }

if __name__ == "__main__":
    result = train_ppo_agent(total_timesteps=500)
    print("PPO Agent Training Result:", result)
