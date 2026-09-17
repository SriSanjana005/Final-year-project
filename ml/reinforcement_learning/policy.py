import numpy as np
from typing import List, Dict, Any

STATE_DIMENSION = 68

class LearnerStateAdapter:
    def __init__(self, state_dim: int = STATE_DIMENSION):
        self.state_dim = state_dim

    def build_observation_vector(
        self,
        transformer_representation: List[float],
        recent_avg_score: float = 0.7,
        completion_rate: float = 0.8,
        recent_time_spent: float = 0.5,
        current_difficulty_str: str = "easy"
    ) -> np.ndarray:
        """
        Combines 64-D Transformer representation with 4 normalized contextual features:
        [transformer_embedding(64d), recent_avg_score, completion_rate, recent_time_spent, current_difficulty]
        Returns 68-dimensional NumPy float32 vector.
        """
        # Ensure representation is exactly 64 dims
        rep = list(transformer_representation)
        if len(rep) < 64:
            rep = rep + [0.0] * (64 - len(rep))
        elif len(rep) > 64:
            rep = rep[:64]

        diff_map = {"easy": 0.33, "medium": 0.66, "hard": 1.0}
        diff_val = diff_map.get(str(current_difficulty_str).lower(), 0.33)

        context_features = [
            max(0.0, min(1.0, float(recent_avg_score))),
            max(0.0, min(1.0, float(completion_rate))),
            max(0.0, min(1.0, float(recent_time_spent))),
            diff_val
        ]

        full_state = rep + context_features
        return np.array(full_state, dtype=np.float32)
