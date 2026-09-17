import os
import sys
import json
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from stable_baselines3 import PPO
from ml.config.training_config import config
from ml.reinforcement_learning.environment import LearnerRecommendationEnv
from ml.reinforcement_learning.actions import ActionType

def evaluate_ppo_agent(episodes: int = 50):
    """
    Evaluates PPO recommendation agent policy across test episodes.
    Computes mean reward, reward variance, and discrete action distribution.
    Saves evaluation metrics to ml/models/ppo/ppo_evaluation_results.json.
    """
    checkpoint_path = os.path.join(config.PPO_MODEL_DIR, "ppo_recommendation_agent.zip")
    if not os.path.exists(checkpoint_path):
        checkpoint_path = os.path.join(PROJECT_ROOT, "ml", "models", "ppo_recommendation_agent.zip")

    if not os.path.exists(checkpoint_path):
        print("Notice: PPO agent checkpoint file missing.")
        return {"status": "checkpoint_missing", "message": "PPO model missing."}

    try:
        model = PPO.load(checkpoint_path)
    except Exception as e:
        print(f"Error loading PPO checkpoint: {e}")
        return {"status": "error", "message": str(e)}

    env = LearnerRecommendationEnv()
    episode_rewards = []
    action_counts = {int(a): 0 for a in ActionType}

    for ep in range(episodes):
        obs, _ = env.reset(seed=config.PPO_SEED + ep)
        done = False
        truncated = False
        ep_reward = 0.0

        while not (done or truncated):
            action, _ = model.predict(obs, deterministic=True)
            action_int = int(action)
            action_counts[action_int] = action_counts.get(action_int, 0) + 1

            obs, reward, done, truncated, _ = env.step(action)
            ep_reward += reward

        episode_rewards.append(ep_reward)

    mean_reward = float(np.mean(episode_rewards))
    std_reward = float(np.std(episode_rewards))

    total_actions = sum(action_counts.values())
    action_dist = {
        ActionType(k).name: round(v / max(1, total_actions), 4) 
        for k, v in action_counts.items()
    }

    results = {
        "evaluation_status": "evaluated",
        "timestamp": os.path.getmtime(checkpoint_path),
        "episodes_evaluated": episodes,
        "mean_episode_reward": round(mean_reward, 4),
        "std_episode_reward": round(std_reward, 4),
        "action_distribution": action_dist,
        "environment_label": "DEVELOPMENT-ONLY TOY ENVIRONMENT — Observational Replay Evaluation"
    }

    os.makedirs(config.PPO_MODEL_DIR, exist_ok=True)
    eval_path = os.path.join(config.PPO_MODEL_DIR, "ppo_evaluation_results.json")
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"PPO Agent Evaluation Completed ({episodes} episodes): Mean Reward = {mean_reward:.4f} +/- {std_reward:.4f}")
    print(f"PPO Action Distribution: {action_dist}")
    print(f"Evaluation results exported to {eval_path}")

    return results

if __name__ == "__main__":
    evaluate_ppo_agent()
