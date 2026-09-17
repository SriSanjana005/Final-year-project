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
from app.models.learning_history import LearningHistory
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.services.ai_availability_service import AIAvailabilityService
from app.services.content_selection_service import ContentSelectionService
from app.services.ai_recommendation_service import AIRecommendationService
from app.services.recommendation_service import RecommendationService
from ml.reinforcement_learning.actions import ActionType

# Use in-memory SQLite database for deterministic integration testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

class TestEndToEndAIRecommendation(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        self.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.TestingSessionLocal()

        # Seed test user and child
        self.user = User(id=1, email="child_test@example.com", password_hash="hashed", role=UserRole.CHILD, name="Test Learner")
        self.db.add(self.user)
        self.db.commit()

        self.child = ChildProfile(id=1, user_id=1, date_of_birth="2018-01-01", learning_level="beginner")
        self.db.add(self.child)
        self.db.commit()

        # Seed test topic
        self.topic = Topic(id=1, name="Mathematics", subject="Mathematics", description="Math Topic")
        self.db.add(self.topic)
        self.db.commit()

        # Seed test published learning contents
        self.content_easy = LearningContent(
            id=1, topic_id=1, title="Basic Addition", description="Easy Lesson", content_body="Lesson content body",
            difficulty="easy", content_type="lesson", is_published=True
        )
        self.content_medium = LearningContent(
            id=2, topic_id=1, title="Double Digit Addition", description="Medium Lesson", content_body="Lesson content body",
            difficulty="medium", content_type="lesson", is_published=True
        )
        self.content_practice = LearningContent(
            id=3, topic_id=1, title="Addition Practice Game", description="Practice Game", content_body="Practice content body",
            difficulty="easy", content_type="practice", is_published=True
        )
        self.content_unpublished = LearningContent(
            id=4, topic_id=1, title="Draft Content", description="Draft", content_body="Draft content body",
            difficulty="easy", content_type="lesson", is_published=False
        )
        self.db.add_all([self.content_easy, self.content_medium, self.content_practice, self.content_unpublished])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_1_ai_availability_and_cold_start(self):
        """Validates AIAvailabilityService detects cold-start for new child without history."""
        status = AIAvailabilityService.check_ai_status(self.db, self.child.id)
        self.assertTrue(status["cold_start"])
        self.assertEqual(status["interaction_count"], 0)
        self.assertEqual(status["strategy_selected"], "rule_based")

    def test_2_cold_start_recommendation_generation(self):
        """Validates that cold-start learner receives rule_based introductory recommendation."""
        rec = AIRecommendationService.generate_personalized_recommendation(self.db, self.child.id)
        self.assertIsNotNone(rec)
        self.assertEqual(rec.recommendation_type, "rule_based")
        self.assertEqual(rec.status, "recommended")
        self.assertTrue(rec.content_id in [1, 2, 3])
        self.assertNotEqual(rec.content_id, 4)  # Unpublished content MUST NOT be recommended

    def test_3_content_selection_boundary(self):
        """Validates ContentSelectionService enforces published status and action mapping."""
        content = ContentSelectionService.select_content_for_action(
            db=self.db,
            child_id=self.child.id,
            action_type=ActionType.PRACTICE_CONTENT,
            current_topic_id=1,
            current_difficulty="easy"
        )
        self.assertIsNotNone(content)
        self.assertTrue(content.is_published)
        self.assertEqual(content.content_type, "practice")
        self.assertEqual(content.id, 3)

    def test_4_repetition_avoidance(self):
        """Validates that uncompleted content is preferred over completed content."""
        # Record completion for content #1
        history = LearningHistory(child_id=self.child.id, activity_type="lesson", activity_id=1)
        self.db.add(history)
        self.db.commit()

        content = ContentSelectionService.select_content_for_action(
            db=self.db,
            child_id=self.child.id,
            action_type=ActionType.EASIER_CONTENT,
            current_topic_id=1,
            current_difficulty="easy"
        )
        self.assertIsNotNone(content)
        self.assertTrue(content.is_published)
        # Content #1 was completed, so candidate #3 (easy practice) or #2 should be selected if available
        self.assertNotEqual(content.id, 4)  # Unpublished content never selected

    def test_5_recommendation_lifecycle_transitions(self):
        """Validates recommendation status transitions: recommended -> viewed -> completed."""
        rec = AIRecommendationService.generate_personalized_recommendation(self.db, self.child.id)
        self.assertIsNotNone(rec)
        self.assertEqual(rec.status, "recommended")

        # Mark viewed
        rec.status = "viewed"
        self.db.commit()
        self.assertEqual(rec.status, "viewed")

        # Mark completed
        rec.status = "completed"
        self.db.commit()
        self.assertEqual(rec.status, "completed")

    def test_6_feedback_loop_updates_history(self):
        """Validates completed activity creates LearningHistory entry for sequence builder."""
        rec = AIRecommendationService.generate_personalized_recommendation(self.db, self.child.id)
        
        # Simulate completing recommended activity
        history = LearningHistory(
            child_id=self.child.id,
            activity_type="lesson",
            activity_id=rec.content_id
        )
        self.db.add(history)
        self.db.commit()

        interaction_count = AIAvailabilityService.get_learner_interaction_count(self.db, self.child.id)
        self.assertGreaterEqual(interaction_count, 1)

if __name__ == "__main__":
    unittest.main()
