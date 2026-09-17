import unittest
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.db.database import SessionLocal
from app.db.seed_test_data import seed_test_data, clear_test_data
from app.models.user import User
from app.models.learning_history import LearningHistory
from app.models.quiz_attempt import QuizAttempt
from app.models.child import ChildProfile

class TestDevelopmentSeeder(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_seeder_execution_and_idempotency(self):
        # 1. Run seeder
        summary = seed_test_data(self.db)
        
        self.assertEqual(summary["test_children_count"], 5)
        self.assertEqual(summary["test_parent_count"], 1)
        self.assertGreaterEqual(summary["learning_interactions_count"], 60)
        self.assertGreaterEqual(summary["quiz_attempts_count"], 60)
        self.assertGreaterEqual(summary["answers_count"], 300)

        # 2. Verify DB state for test users
        test_users = self.db.query(User).filter(User.is_test_data == True).all()
        self.assertEqual(len(test_users), 6) # 5 children + 1 parent

        # 3. Verify cold start learner has < 3 interactions
        cold_user = self.db.query(User).filter(User.email == "test.child.cold@example.com").first()
        self.assertIsNotNone(cold_user)
        cold_child = self.db.query(ChildProfile).filter(ChildProfile.user_id == cold_user.id).first()
        self.assertIsNotNone(cold_child)
        cold_interactions = self.db.query(LearningHistory).filter(LearningHistory.child_id == cold_child.id).count()
        self.assertLess(cold_interactions, 3)

        # 4. Re-run seeder to verify idempotency (no duplicate count accumulation)
        summary2 = seed_test_data(self.db)
        test_users_after = self.db.query(User).filter(User.is_test_data == True).all()
        self.assertEqual(len(test_users_after), 6)
        self.assertEqual(summary2["learning_interactions_count"], summary["learning_interactions_count"])

if __name__ == "__main__":
    unittest.main()
