import unittest
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.db.seed_test_data import seed_test_data
from app.models.user import User
from app.models.child import ChildProfile
from app.models.parent import ParentProfile
from app.models.parent_child import ParentChild
from app.models.quiz_attempt import QuizAttempt, Answer
from app.models.learning_history import LearningHistory
from app.models.recommendation import Recommendation
from ml.evaluation.dataset import EvaluationDatasetExtractor

class TestBackendEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Seed development test dataset once for the test suite."""
        cls.db = SessionLocal()
        seed_test_data(cls.db)
        cls.client = TestClient(app)

        # Helper function to obtain JWT token for given user email & password
        def get_auth_token(email: str, password: str = "DevTest123!") -> str:
            res = cls.client.post("/api/auth/login", json={"email": email, "password": password})
            if res.status_code != 200:
                # Try admin password fallback
                res = cls.client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
            assert res.status_code == 200, f"Login failed for {email}: {res.text}"
            return res.json()["access_token"]

        cls.parent_token = get_auth_token("test.parent@example.com")
        cls.child_low_token = get_auth_token("test.child.low@example.com")
        cls.child_high_token = get_auth_token("test.child.high@example.com")
        cls.child_cold_token = get_auth_token("test.child.cold@example.com")
        cls.admin_token = get_auth_token("admin@example.com", "Password123!")

        # Retrieve profile IDs
        cls.low_child_user = cls.db.query(User).filter(User.email == "test.child.low@example.com").first()
        cls.low_child_prof = cls.db.query(ChildProfile).filter(ChildProfile.user_id == cls.low_child_user.id).first()

        cls.high_child_user = cls.db.query(User).filter(User.email == "test.child.high@example.com").first()
        cls.high_child_prof = cls.db.query(ChildProfile).filter(ChildProfile.user_id == cls.high_child_user.id).first()

        cls.cold_child_user = cls.db.query(User).filter(User.email == "test.child.cold@example.com").first()
        cls.cold_child_prof = cls.db.query(ChildProfile).filter(ChildProfile.user_id == cls.cold_child_user.id).first()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    # -------------------------------------------------------------
    # 1. AUTHENTICATION E2E TESTS
    # -------------------------------------------------------------
    def test_01_login_valid_credentials(self):
        res = self.client.post("/api/auth/login", json={
            "email": "test.child.low@example.com",
            "password": "DevTest123!"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
        self.assertEqual(data["user"]["role"], "child")

    def test_02_login_invalid_password(self):
        res = self.client.post("/api/auth/login", json={
            "email": "test.child.low@example.com",
            "password": "WrongPassword!"
        })
        self.assertEqual(res.status_code, 401)

    def test_03_login_nonexistent_user(self):
        res = self.client.post("/api/auth/login", json={
            "email": "nonexistent.user.999@example.com",
            "password": "Password123!"
        })
        self.assertEqual(res.status_code, 401)

    def test_04_get_auth_me(self):
        headers = {"Authorization": f"Bearer {self.child_low_token}"}
        res = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["email"], "test.child.low@example.com")
        self.assertEqual(data["role"], "child")

    # -------------------------------------------------------------
    # 2. ROLE AUTHORIZATION TESTS
    # -------------------------------------------------------------
    def test_05_child_blocked_from_admin_endpoints(self):
        headers = {"Authorization": f"Bearer {self.child_low_token}"}
        res = self.client.get("/api/users", headers=headers)
        self.assertEqual(res.status_code, 403)

        res2 = self.client.get("/api/admin/metrics", headers=headers)
        self.assertEqual(res2.status_code, 403)

        res3 = self.client.get("/api/recommendations/admin/evaluation/summary", headers=headers)
        self.assertEqual(res3.status_code, 403)

    def test_06_parent_blocked_from_admin_endpoints(self):
        headers = {"Authorization": f"Bearer {self.parent_token}"}
        res = self.client.get("/api/users", headers=headers)
        self.assertEqual(res.status_code, 403)

        res2 = self.client.get("/api/parent-child", headers=headers)
        self.assertEqual(res2.status_code, 403)

    def test_07_child_cannot_access_other_child_history(self):
        headers = {"Authorization": f"Bearer {self.child_low_token}"}
        # Attempting to access High Child's history using Low Child's token
        res = self.client.get(f"/api/history/child/{self.high_child_prof.id}", headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_08_admin_access_allowed(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        res = self.client.get("/api/users", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)

    # -------------------------------------------------------------
    # 3. CHILD LEARNING & CONTENT FLOW
    # -------------------------------------------------------------
    def test_09_get_active_topics(self):
        headers = {"Authorization": f"Bearer {self.child_low_token}"}
        res = self.client.get("/api/topics", headers=headers)
        self.assertEqual(res.status_code, 200)
        topics = res.json()
        self.assertGreaterEqual(len(topics), 4)

    def test_10_get_published_content(self):
        headers = {"Authorization": f"Bearer {self.child_low_token}"}
        res = self.client.get("/api/content/published", headers=headers)
        self.assertEqual(res.status_code, 200)
        contents = res.json()
        self.assertGreaterEqual(len(contents), 10)
        for c in contents:
            self.assertTrue(c["is_published"])

    # -------------------------------------------------------------
    # 4. QUIZ FLOW & BACKEND SCORE CALCULATION
    # -------------------------------------------------------------
    def test_11_get_published_quizzes(self):
        res = self.client.get("/api/quizzes/published")
        self.assertEqual(res.status_code, 200)
        quizzes = res.json()
        self.assertGreaterEqual(len(quizzes), 4)

    def test_12_get_quiz_for_attempt_hides_answers(self):
        headers = {"Authorization": f"Bearer {self.child_low_token}"}
        res = self.client.get("/api/quizzes/published")
        quiz_id = res.json()[0]["id"]

        attempt_res = self.client.get(f"/api/quizzes/{quiz_id}/attempt", headers=headers)
        self.assertEqual(attempt_res.status_code, 200)
        quiz_data = attempt_res.json()
        self.assertIn("questions", quiz_data)
        for q in quiz_data["questions"]:
            self.assertNotIn("correct_answer", q)
            self.assertNotIn("explanation", q)

    def test_13_quiz_submission_e2e(self):
        headers = {"Authorization": f"Bearer {self.child_high_token}"}
        res = self.client.get("/api/quizzes/published")
        quiz_id = res.json()[0]["id"]

        attempt_res = self.client.get(f"/api/quizzes/{quiz_id}/attempt", headers=headers)
        questions = attempt_res.json()["questions"]

        # Submit answers
        submission_payload = {
            "answers": [{"question_id": q["id"], "selected_answer": "B"} for q in questions]
        }

        submit_res = self.client.post(f"/api/quizzes/{quiz_id}/submit", json=submission_payload, headers=headers)
        self.assertEqual(submit_res.status_code, 200)
        sub_data = submit_res.json()

        self.assertIn("attempt_id", sub_data)
        self.assertIn("percentage", sub_data)
        self.assertIn("score", sub_data)
        self.assertEqual(sub_data["total_questions"], len(questions))

        # Verify QuizAttempt & LearningHistory in DB
        attempt_db = self.db.query(QuizAttempt).filter(QuizAttempt.id == sub_data["attempt_id"]).first()
        self.assertIsNotNone(attempt_db)
        self.assertEqual(attempt_db.child_id, self.high_child_prof.id)

        answers_db = self.db.query(Answer).filter(Answer.attempt_id == sub_data["attempt_id"]).all()
        self.assertEqual(len(answers_db), len(questions))

    # -------------------------------------------------------------
    # 5. LEARNING HISTORY ENDPOINTS
    # -------------------------------------------------------------
    def test_14_get_child_learning_history(self):
        headers = {"Authorization": f"Bearer {self.child_low_token}"}
        res = self.client.get(f"/api/history/child/{self.low_child_prof.id}", headers=headers)
        self.assertEqual(res.status_code, 200)
        history = res.json()
        self.assertGreaterEqual(len(history), 10)
        for item in history:
            self.assertEqual(item["child_id"], self.low_child_prof.id)
            self.assertIn("activity_type", item)
            self.assertIn("score", item)

    # -------------------------------------------------------------
    # 6. RECOMMENDATION GENERATION & COLD-START FALLBACK
    # -------------------------------------------------------------
    def test_15_ai_status_check(self):
        headers = {"Authorization": f"Bearer {self.child_low_token}"}
        res = self.client.get("/api/recommendations/ai-status", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("strategy_selected", data)
        self.assertIn("cold_start", data)

    def test_16_generate_recommendation_established_learner(self):
        headers = {"Authorization": f"Bearer {self.child_high_token}"}
        res = self.client.post("/api/recommendations/generate", headers=headers)
        self.assertEqual(res.status_code, 200)
        rec = res.json()
        self.assertIn("content_id", rec)
        self.assertIn("recommendation_type", rec)
        self.assertIn(rec["recommendation_type"], ["rule_based", "transformer_ppo"])
        self.assertIsNotNone(rec["reason"])

    def test_17_generate_recommendation_cold_start_learner(self):
        headers = {"Authorization": f"Bearer {self.child_cold_token}"}
        res = self.client.post("/api/recommendations/generate", headers=headers)
        self.assertEqual(res.status_code, 200)
        rec = res.json()
        self.assertEqual(rec["recommendation_type"], "rule_based")

    def test_18_recommendation_lifecycle(self):
        headers = {"Authorization": f"Bearer {self.child_low_token}"}
        res = self.client.post("/api/recommendations/generate", headers=headers)
        rec_id = res.json()["id"]

        # View recommendation
        view_res = self.client.post(f"/api/recommendations/{rec_id}/view", headers=headers)
        self.assertEqual(view_res.status_code, 200)
        self.assertEqual(view_res.json()["status"], "viewed")

        # Complete recommendation
        complete_res = self.client.post(f"/api/recommendations/{rec_id}/complete", headers=headers)
        self.assertEqual(complete_res.status_code, 200)
        self.assertEqual(complete_res.json()["status"], "completed")

    # -------------------------------------------------------------
    # 7. PARENT FLOW & ACCESS CONTROLS
    # -------------------------------------------------------------
    def test_19_parent_get_linked_children(self):
        headers = {"Authorization": f"Bearer {self.parent_token}"}
        res = self.client.get("/api/parents/me/children", headers=headers)
        self.assertEqual(res.status_code, 200)
        children = res.json()
        self.assertEqual(len(children), 5)

    def test_20_parent_view_linked_child_progress(self):
        headers = {"Authorization": f"Bearer {self.parent_token}"}
        res = self.client.get(f"/api/progress/child/{self.low_child_prof.id}", headers=headers)
        self.assertEqual(res.status_code, 200)
        progress = res.json()
        self.assertEqual(progress["child_id"], self.low_child_prof.id)
        self.assertGreaterEqual(progress["total_quizzes_completed"], 10)

    # -------------------------------------------------------------
    # 8. ADMIN DASHBOARD & EVALUATION SUMMARY
    # -------------------------------------------------------------
    def test_21_admin_metrics_endpoint(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        res = self.client.get("/api/admin/metrics", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["total_users"], 6)
        self.assertGreaterEqual(data["total_children"], 5)

    def test_22_admin_evaluation_summary(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        res = self.client.get("/api/recommendations/admin/evaluation/summary", headers=headers)
        self.assertEqual(res.status_code, 200)
        summary = res.json()
        self.assertIn("evaluation_status", summary)

    # -------------------------------------------------------------
    # 9. EVALUATION DATA ISOLATION
    # -------------------------------------------------------------
    def test_23_evaluation_dataset_isolation(self):
        rule_recs, proposed_recs, safety_audit = EvaluationDatasetExtractor.extract_evaluation_records(self.db)
        # Verify development test data is excluded from official research evaluation metrics
        for r in rule_recs + proposed_recs:
            rec_db = self.db.query(Recommendation).filter(Recommendation.id == r["id"]).first()
            if rec_db:
                self.assertFalse(rec_db.is_test_data)

    # -------------------------------------------------------------
    # 10. ERROR HANDLING & SECURITY BOUNDARIES
    # -------------------------------------------------------------
    def test_24_invalid_bearer_token(self):
        headers = {"Authorization": "Bearer InvalidTokenString12345"}
        res = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(res.status_code, 401)

    def test_25_missing_resource_not_found(self):
        headers = {"Authorization": f"Bearer {self.child_low_token}"}
        res = self.client.get("/api/content/999999", headers=headers)
        self.assertEqual(res.status_code, 404)

    def test_26_post_test_database_integrity(self):
        # Verify zero orphan quiz attempt answers
        orphan_answers = self.db.query(Answer).filter(
            ~Answer.attempt_id.in_(self.db.query(QuizAttempt.id))
        ).count()
        self.assertEqual(orphan_answers, 0)

        # Verify zero orphan learning histories
        orphan_histories = self.db.query(LearningHistory).filter(
            ~LearningHistory.child_id.in_(self.db.query(ChildProfile.id))
        ).count()
        self.assertEqual(orphan_histories, 0)

if __name__ == "__main__":
    unittest.main()
