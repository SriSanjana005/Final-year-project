import os
import sys
import unittest

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
from app.models.recommendation import Recommendation
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt

from ml.evaluation.config import eval_config
from ml.evaluation.dataset import EvaluationDatasetExtractor
from ml.evaluation.metrics import compute_strategy_metrics, compute_confidence_interval
from ml.evaluation.comparison import StrategyComparator
from ml.evaluation.report import EvaluationReportGenerator
from ml.evaluation.evaluator import run_evaluation_pipeline

class TestEvaluationFramework(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        self.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.TestingSessionLocal()

        # Seed test user and child
        self.user = User(id=1, email="eval_learner@example.com", password_hash="hashed", role=UserRole.CHILD, name="Eval Learner")
        self.db.add(self.user)
        self.db.commit()

        self.child = ChildProfile(id=1, user_id=1, date_of_birth="2018-01-01", learning_level="beginner")
        self.db.add(self.child)
        self.db.commit()

        # Seed topic and published content
        self.topic = Topic(id=1, name="Math", subject="Math", description="Math Topic", is_active=True)
        self.db.add(self.topic)
        self.db.commit()

        self.content = LearningContent(
            id=1, topic_id=1, title="Addition Module", description="Desc", content_body="Body",
            difficulty="easy", content_type="lesson", is_published=True
        )
        self.db.add(self.content)
        self.db.commit()

        # Seed Rule-Based Recommendation
        self.rec1 = Recommendation(
            id=1, child_id=1, content_id=1, topic_id=1, target_difficulty="easy",
            reason="Rule recommendation", recommendation_type="rule_based", status="completed", avg_score=80.0
        )

        # Seed Transformer+PPO Recommendation
        self.rec2 = Recommendation(
            id=2, child_id=1, content_id=1, topic_id=1, target_difficulty="easy",
            reason="AI recommendation", recommendation_type="transformer_ppo", status="viewed", avg_score=85.0
        )
        self.db.add_all([self.rec1, self.rec2])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_1_dataset_extraction_and_safety_audit(self):
        """Validates strategy separation and content safety audit."""
        rb_recs, pr_recs, safety = EvaluationDatasetExtractor.extract_evaluation_records(self.db)
        self.assertEqual(len(rb_recs), 1)
        self.assertEqual(len(pr_recs), 1)
        self.assertEqual(safety["total_recommendations"], 2)
        self.assertEqual(safety["approved_content_recommendations"], 2)
        self.assertEqual(safety["invalid_recommendations"], 0)
        self.assertTrue(safety["integrity_passed"])

    def test_2_metrics_computation(self):
        """Validates metric calculations (view rate, completion rate, alignment)."""
        rb_recs, pr_recs, _ = EvaluationDatasetExtractor.extract_evaluation_records(self.db)
        rb_metrics = compute_strategy_metrics(rb_recs)
        pr_metrics = compute_strategy_metrics(pr_recs)

        self.assertEqual(rb_metrics["completion_rate"], 100.0)
        self.assertEqual(pr_metrics["completion_rate"], 0.0)
        self.assertEqual(pr_metrics["view_rate"], 100.0)

    def test_3_confidence_interval_math(self):
        """Validates statistical confidence interval calculation."""
        scores = [80.0, 85.0, 90.0]
        ci = compute_confidence_interval(scores)
        self.assertEqual(ci["mean"], 85.0)
        self.assertEqual(ci["sample_size"], 3)

    def test_4_comparison_matrix_builder(self):
        """Validates side-by-side neutral comparison table format."""
        rb_recs, pr_recs, _ = EvaluationDatasetExtractor.extract_evaluation_records(self.db)
        rb_m = compute_strategy_metrics(rb_recs)
        pr_m = compute_strategy_metrics(pr_recs)
        
        comp = StrategyComparator.build_comparison_matrix(rb_m, pr_m)
        matrix = comp["comparison_matrix"]
        self.assertGreater(len(matrix), 0)
        self.assertIn("metric_name", matrix[0])
        self.assertIn("rule_based", matrix[0])
        self.assertIn("transformer_ppo", matrix[0])

    def test_5_evaluation_pipeline_execution(self):
        """Validates complete evaluation pipeline execution and export."""
        results = run_evaluation_pipeline(self.db)
        self.assertEqual(results["evaluation_status"], "completed")
        self.assertIn("content_safety_audit", results)
        self.assertIn("baseline_metrics", results)
        self.assertIn("proposed_metrics", results)

if __name__ == "__main__":
    unittest.main()
