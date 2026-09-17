import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_ROOT = os.path.join(PROJECT_ROOT, "backend")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)


import unittest
import torch
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, Base, engine
from app.models import User, UserRole, ChildProfile, LearningHistory, QuizAttempt, Quiz

from ml.data.sequence_builder import SequenceBuilder
from ml.data.feature_encoder import FeatureEncoder
from ml.transformer.config import TransformerConfig
from ml.transformer.model import LearnerTransformerEncoder
from ml.transformer.inference import LearnerStateExtractor
from backend.app.services.transformer_service import TransformerService

class TestMLPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db: Session = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_feature_encoder(self):
        encoder = FeatureEncoder(max_seq_len=20)
        sample_seq = [
            {"topic_id": 1, "difficulty": "easy", "activity_type": "lesson", "completion_status": "completed", "score": 85.0, "time_spent": 120},
            {"topic_id": 1, "difficulty": "medium", "activity_type": "quiz", "completion_status": "completed", "score": 90.0, "time_spent": 180}
        ]
        tensors = encoder.encode_sequence(sample_seq)

        self.assertEqual(tensors["topic_ids"].shape[0], 20)
        self.assertEqual(tensors["scores"].shape[0], 20)
        self.assertEqual(tensors["padding_mask"].shape[0], 20)
        
        # 18 padded steps (True) and 2 valid steps (False)
        self.assertEqual(tensors["padding_mask"].sum().item(), 18)

    def test_02_transformer_forward_pass(self):
        config = TransformerConfig()
        model = LearnerTransformerEncoder(config)
        model.eval()

        encoder = FeatureEncoder(max_seq_len=20)
        sample_seq = [
            {"topic_id": 1, "difficulty": "easy", "activity_type": "lesson", "completion_status": "completed", "score": 85.0, "time_spent": 120}
        ]
        tensors = encoder.encode_sequence(sample_seq)
        
        # Add batch dimension [1, 20]
        batch = {k: v.unsqueeze(0) for k, v in tensors.items()}

        with torch.no_grad():
            learner_rep = model(batch)

        self.assertEqual(learner_rep.shape, torch.Size([1, 64]))

    def test_03_transformer_service_learner_state(self):
        child = self.db.query(ChildProfile).first()
        if child:
            res = TransformerService.get_learner_state(self.db, child_id=child.id)
            self.assertIn(res["model_status"], ["available", "cold_start"])
            self.assertEqual(res["representation_dimension"], 64)

    def test_04_cold_start_handling(self):
        res = TransformerService.get_learner_state(self.db, child_id=999999) # Non-existent child
        self.assertEqual(res["model_status"], "error")

if __name__ == "__main__":
    unittest.main()
