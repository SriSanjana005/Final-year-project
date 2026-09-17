import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Tuple, Dict, Any, Optional
from ml.reinforcement_learning.actions import ActionType
from ml.reinforcement_learning.policy import LearnerStateAdapter, STATE_DIMENSION
from ml.reinforcement_learning.reward import LearnerRewardCalculator

class LearnerRecommendationEnv(gym.Env):
    """
    Gymnasium-compatible offline simulation environment representing the learner recommendation process.
    Used for PPO model initialization and offline policy evaluation.
    """
    metadata = {"render_modes": []}

    def __init__(self, initial_state: Optional[np.ndarray] = None):
        super().__init__()
        
        self.state_adapter = LearnerStateAdapter()
        self.reward_calculator = LearnerRewardCalculator()

        # Observation Space: 68-D continuous float vector
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(STATE_DIMENSION,),
            dtype=np.float32
        )

        # Action Space: 5 Discrete Actions (0: REVIEW, 1: EASIER, 2: SAME, 3: HARDER, 4: PRACTICE)
        self.action_space = spaces.Discrete(5)

        self.current_step = 0
        self.max_steps = 10
        self.state = initial_state if initial_state is not None else self._get_default_state()
        self.prev_score = 70.0

    @staticmethod
    def _get_default_state() -> np.ndarray:
        dummy_rep = [0.0] * 64
        return LearnerStateAdapter().build_observation_vector(
            transformer_representation=dummy_rep,
            recent_avg_score=0.7,
            completion_rate=0.8,
            recent_time_spent=0.5,
            current_difficulty_str="easy"
        )


    def reset(self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        super().reset(seed=seed)
        self.current_step = 0
        self.prev_score = 70.0
        self.state = self._get_default_state()
        return self.state, {"message": "Environment reset complete."}

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        self.current_step += 1
        act = ActionType(action)

        # Simulate state transition and outcome based on action type
        if act == ActionType.EASIER_CONTENT:
            sim_current_score = min(100.0, self.prev_score + 10.0)
            target_diff = "easy"
        elif act == ActionType.HARDER_CONTENT:
            sim_current_score = max(40.0, self.prev_score - 5.0)
            target_diff = "hard"
        elif act == ActionType.REVIEW_PREVIOUS_TOPIC:
            sim_current_score = min(100.0, self.prev_score + 15.0)
            target_diff = "easy"
        else: # SAME_DIFFICULTY or PRACTICE_CONTENT
            sim_current_score = self.prev_score + 5.0
            target_diff = "medium"

        reward = self.reward_calculator.calculate_reward(
            prev_score=self.prev_score,
            current_score=sim_current_score,
            completed=True,
            time_spent_seconds=120,
            target_difficulty=target_diff,
            learner_level="beginner"
        )

        self.prev_score = sim_current_score
        terminated = self.current_step >= self.max_steps
        truncated = False

        # Next observation vector
        dummy_rep = np.random.normal(0, 0.1, 64).tolist()
        next_obs = self.state_adapter.build_observation_vector(
            transformer_representation=dummy_rep,
            recent_avg_score=sim_current_score / 100.0,
            completion_rate=0.9,
            recent_time_spent=0.4,
            current_difficulty_str=target_diff
        )
        self.state = next_obs

        info = {
            "action": action,
            "action_name": act.name,
            "simulated_score": sim_current_score,
            "step": self.current_step
        }

        return next_obs, reward, terminated, truncated, info
