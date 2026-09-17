from typing import Dict, Any

class LearnerRewardCalculator:
    def __init__(
        self,
        w_improvement: float = 1.0,
        w_completion: float = 0.5,
        w_engagement: float = 0.2,
        w_penalty: float = 0.5
    ):
        self.w_improvement = w_improvement
        self.w_completion = w_completion
        self.w_engagement = w_engagement
        self.w_penalty = w_penalty

    def calculate_reward(
        self,
        prev_score: float,
        current_score: float,
        completed: bool,
        time_spent_seconds: int,
        target_difficulty: str,
        learner_level: str
    ) -> float:
        """
        Calculates experimental RL scalar reward signal:
        reward = R_improvement + R_completion + R_engagement - P_inappropriate_difficulty
        """
        # 1. Performance Improvement Signal (-1.0 to +1.0)
        score_diff = (current_score - prev_score) / 100.0
        r_improvement = self.w_improvement * score_diff

        # 2. Completion Signal
        r_completion = self.w_completion if completed else -0.2

        # 3. Engagement Signal (modest bonus for sustained effort > 30s)
        r_engagement = self.w_engagement if time_spent_seconds >= 30 else 0.0

        # 4. Inappropriate Difficulty Penalty
        p_difficulty = 0.0
        if learner_level == "beginner" and target_difficulty == "hard":
            p_difficulty = self.w_penalty
        elif learner_level == "advanced" and target_difficulty == "easy" and current_score < 60:
            p_difficulty = self.w_penalty * 0.5

        total_reward = r_improvement + r_completion + r_engagement - p_difficulty
        return round(float(total_reward), 4)
