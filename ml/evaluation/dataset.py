import sys
import os
from typing import List, Dict, Any, Tuple
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.recommendation import Recommendation
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz import Quiz
from app.models.learning_history import LearningHistory
from app.models.content import LearningContent
from app.models.topic import Topic

class EvaluationDatasetExtractor:
    @staticmethod
    def extract_evaluation_records(db: Session = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        """
        Extracts recommendation logs paired with subsequent learner outcomes.
        Separates records strictly into rule_based and transformer_ppo subsets.
        Performs content safety integrity audit.
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        rule_based_records = []
        proposed_records = []

        total_recs = 0
        approved_content_recs = 0
        invalid_recs = 0

        try:
            recs = db.query(Recommendation).order_by(Recommendation.generated_at.asc()).all()
            # Exclude development test data from official FYP research evaluation metrics
            recs = [r for r in recs if not getattr(r, 'is_test_data', False)]
            total_recs = len(recs)

            for r in recs:
                # 1. Content Safety Audit
                content = db.query(LearningContent).filter(LearningContent.id == r.content_id).first()
                topic = db.query(Topic).filter(Topic.id == r.topic_id).first() if r.topic_id else None

                is_safe = (
                    content is not None and 
                    content.is_published == True and 
                    (topic is None or topic.is_active == True)
                )

                if is_safe:
                    approved_content_recs += 1
                else:
                    invalid_recs += 1

                # 2. Subsequent Quiz Outcome Matching
                subsequent_attempt = (
                    db.query(QuizAttempt)
                    .filter(
                        QuizAttempt.child_id == r.child_id,
                        QuizAttempt.completed_at >= r.generated_at
                    )
                    .order_by(QuizAttempt.completed_at.asc())
                    .first()
                )

                previous_attempt = (
                    db.query(QuizAttempt)
                    .filter(
                        QuizAttempt.child_id == r.child_id,
                        QuizAttempt.completed_at < r.generated_at
                    )
                    .order_by(QuizAttempt.completed_at.desc())
                    .first()
                )

                subsequent_score = subsequent_attempt.percentage if subsequent_attempt else None
                previous_score = previous_attempt.percentage if previous_attempt else None

                perf_change = None
                if subsequent_score is not None and previous_score is not None:
                    perf_change = subsequent_score - previous_score

                # 3. Repetition Check
                prior_recs_count = (
                    db.query(Recommendation)
                    .filter(
                        Recommendation.child_id == r.child_id,
                        Recommendation.content_id == r.content_id,
                        Recommendation.generated_at < r.generated_at
                    )
                    .count()
                )
                is_repeated = prior_recs_count > 0

                # 4. Difficulty Alignment Check
                is_difficulty_aligned = (
                    content is not None and content.difficulty == r.target_difficulty
                )

                rec_dict = {
                    "id": r.id,
                    "child_id": r.child_id,
                    "content_id": r.content_id,
                    "topic_id": r.topic_id,
                    "difficulty": r.target_difficulty,
                    "recommendation_type": r.recommendation_type,
                    "status": r.status,
                    "is_viewed": r.status in ["viewed", "completed"],
                    "is_completed": r.status == "completed",
                    "subsequent_score": subsequent_score,
                    "previous_score": previous_score,
                    "performance_change": perf_change,
                    "is_repeated": is_repeated,
                    "is_difficulty_aligned": is_difficulty_aligned,
                    "generated_at": r.generated_at.isoformat() if r.generated_at else None
                }

                if r.recommendation_type == "transformer_ppo":
                    proposed_records.append(rec_dict)
                else:
                    rule_based_records.append(rec_dict)

        finally:
            if close_db:
                db.close()

        safety_audit = {
            "total_recommendations": total_recs,
            "approved_content_recommendations": approved_content_recs,
            "invalid_recommendations": invalid_recs,
            "integrity_passed": invalid_recs == 0
        }

        return rule_based_records, proposed_records, safety_audit
