import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_ROOT = os.path.join(PROJECT_ROOT, "backend")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

import unittest
import numpy as np
import torch
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, Base, engine
from app.models import ChildProfile, Recommendation
from ml.reinforcement_learning.actions import ActionType, get_action_description
from ml.reinforcement_learning.policy import LearnerStateAdapter, STATE_DIMENSION
from ml.reinforcement_learning.reward import LearnerRewardCalculator
from ml.reinforcement_learning.environment import LearnerRecommendationEnv
from app.services.rl_recommendation_service import RLRecommendationService
from app.services.recommendation_service import RecommendationService

class TestRLPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db: Session = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_action_space_definitions(self):
        self.assertEqual(int(ActionType.REVIEW_PREVIOUS_TOPIC), 0)
        self.assertEqual(int(ActionType.EASIER_CONTENT), 1)
        self.assertEqual(int(ActionType.SAME_DIFFICULTY), 2)
        self.assertEqual(int(ActionType.HARDER_CONTENT), 3)
        self.assertEqual(int(ActionType.PRACTICE_CONTENT), 4)

        desc = get_action_description(ActionType.HARDER_CONTENT)
        self.assertTrue(len(desc) > 0)

    def test_02_observation_adapter(self):
        adapter = LearnerStateAdapter()
        dummy_rep = [0.1] * 64
        obs = adapter.build_observation_vector(dummy_rep, 0.85, 0.9, 0.4, "medium")

        self.assertEqual(obs.shape, (68,))
        self.assertEqual(obs.dtype, np.float32)

    def test_03_reward_calculator(self):
        calc = LearnerRewardCalculator()
        reward = calc.calculate_reward(
            prev_score=60.0,
            current_score=85.0,
            completed=True,
            time_spent_seconds=60,
            target_difficulty="medium",
            learner_level="beginner"
        )
        self.assertIsInstance(reward, float)
        self.assertTrue(reward > 0.0)

    def test_04_gymnasium_environment(self):
        env = LearnerRecommendationEnv()
        obs, info = env.reset()
        self.assertEqual(obs.shape, (68,))

        next_obs, reward, terminated, truncated, info = env.step(ActionType.EASIER_CONTENT)
        self.assertEqual(next_obs.shape, (68,))
        self.assertIsInstance(reward, float)
        self.assertIn("action_name", info)

    def test_05_rl_recommendation_service(self):
        child = self.db.query(ChildProfile).first()
        if child:
            rec = RecommendationService.generate_recommendation(self.db, child.id)
            self.assertIsNotNone(rec)
            self.assertIn(rec.recommendation_type, ["transformer_ppo", "rule_based"])

    def test_06_cold_start_fallback(self):
        child_id = 999999 # Non-existent child
        rec = RLRecommendationService.generate_ppo_recommendation(self.db, child_id)
        self.assertIsNone(rec) # Should return None to trigger rule-based fallback

if __name__ == "__main__":
    unittest.main()
