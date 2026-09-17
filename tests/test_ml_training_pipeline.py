import os
import sys
import unittest
import torch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.models.user import User, UserRole
from app.models.child import ChildProfile
from app.models.topic import Topic
from app.models.content import LearningContent
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.learning_history import LearningHistory

from ml.config.training_config import config
from ml.data.extract_dataset import extract_learner_interactions
from ml.data.data_quality import run_data_quality_audit
from ml.data.split_dataset import split_learner_dataset
from ml.transformer.dataset import LearnerSequenceDataset, get_performance_tier
from ml.transformer.train import train_transformer_model
from ml.transformer.evaluate import evaluate_transformer_model
from ml.reinforcement_learning.train import train_ppo_agent
from ml.reinforcement_learning.evaluate import evaluate_ppo_agent
from ml.visualization.generate_plots import generate_experiment_plots
from app.services.ai_availability_service import AIAvailabilityService

class TestMLTrainingPipeline(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        self.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.TestingSessionLocal()

        # Seed test user and child
        self.user = User(id=1, email="learner_ml@example.com", password_hash="hashed", role=UserRole.CHILD, name="Learner ML")
        self.db.add(self.user)
        self.db.commit()

        self.child = ChildProfile(id=1, user_id=1, date_of_birth="2018-01-01", learning_level="beginner")
        self.db.add(self.child)
        self.db.commit()

        # Seed topic
        self.topic = Topic(id=1, name="Mathematics", subject="Mathematics", description="Math Topic")
        self.db.add(self.topic)
        self.db.commit()

        # Seed histories & attempts for dataset extraction
        for i in range(5):
            history = LearningHistory(
                child_id=1,
                activity_type="lesson",
                activity_id=i + 1,
                topic_id=1,
                difficulty="easy" if i < 3 else "medium",
                score=70.0 + (i * 5),
                completion_status="completed",
                time_spent=60.0 + (i * 10)
            )
            self.db.add(history)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_1_performance_tier_mapping(self):
        """Validates score classification into target tiers (0: LOW, 1: MEDIUM, 2: HIGH)."""
        self.assertEqual(get_performance_tier(45.0), 0)
        self.assertEqual(get_performance_tier(75.0), 1)
        self.assertEqual(get_performance_tier(85.0), 2)

    def test_2_data_quality_audit(self):
        """Validates Data Quality Audit script identifies record validity."""
        test_records = [
            {"child_id": 1, "topic_id": 1, "difficulty": "easy", "activity_type": "lesson", "score": 80.0, "time_spent": 60, "timestamp": "2026-01-01T10:00:00"},
            {"child_id": 1, "topic_id": 1, "difficulty": "invalid_diff", "activity_type": "lesson", "score": -10.0, "time_spent": 60, "timestamp": "2026-01-01T10:05:00"}
        ]
        report, valid_list = run_data_quality_audit(test_records)
        self.assertEqual(report["total_records"], 2)
        self.assertEqual(report["valid_records"], 1)
        self.assertEqual(len(valid_list), 1)

    def test_3_chronological_dataset_splitter(self):
        """Validates chronological train/val/test splitting."""
        test_records = [
            {"child_id": 1, "topic_id": 1, "score": 60.0, "timestamp": f"2026-01-01T10:0{i}:00"} for i in range(5)
        ]
        train_recs, val_recs, test_recs = split_learner_dataset(test_records, train_ratio=0.60, val_ratio=0.20)
        self.assertGreaterEqual(len(train_recs), 1)
        self.assertGreaterEqual(len(val_recs) + len(test_recs), 1)

    def test_4_pytorch_sequence_dataset_tensors(self):
        """Validates PyTorch LearnerSequenceDataset tensor shapes."""
        test_records = [
            {"child_id": 1, "topic_id": 1, "difficulty": "easy", "activity_type": "lesson", "score": 75.0, "time_spent": 60, "timestamp": f"2026-01-01T10:0{i}:00"} for i in range(3)
        ]
        dataset = LearnerSequenceDataset(test_records, max_seq_len=20)
        self.assertGreater(len(dataset), 0)
        sample = dataset[0]
        self.assertEqual(sample["topic_ids"].shape[0], 20)
        self.assertEqual(sample["scores"].shape[0], 20)
        self.assertIn("target", sample)

    def test_5_transformer_training_and_evaluation_pipeline(self):
        """Validates PyTorch Transformer model supervised training and evaluation execution."""
        meta = train_transformer_model()
        self.assertIn(meta.get("training_status"), ["trained", "insufficient_data"])

        eval_res = evaluate_transformer_model()
        self.assertIn("evaluation_status", eval_res)

    def test_6_ppo_training_and_evaluation_pipeline(self):
        """Validates PPO RL training script and evaluation."""
        ppo_meta = train_ppo_agent(total_timesteps=128)
        self.assertEqual(ppo_meta.get("training_status"), "trained")

        ppo_eval = evaluate_ppo_agent(episodes=2)
        self.assertEqual(ppo_eval.get("evaluation_status"), "evaluated")

    def test_7_backend_ai_status_reporting(self):
        """Validates backend AIAvailabilityService reports truthful model status."""
        status = AIAvailabilityService.check_ai_status(self.db, 1)
        self.assertIn("transformer_details", status)
        self.assertIn("ppo_details", status)
        self.assertIn(status["transformer_details"]["status"], ["trained", "initialized", "unavailable"])
        self.assertIn(status["ppo_details"]["status"], ["trained", "initialized", "unavailable"])

if __name__ == "__main__":
    unittest.main()
