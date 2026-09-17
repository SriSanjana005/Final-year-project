from typing import List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.learning_history import LearningHistory
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz import Quiz

MAX_SEQUENCE_LENGTH = 20

class SequenceBuilder:
    def __init__(self, max_seq_len: int = MAX_SEQUENCE_LENGTH):
        self.max_seq_len = max_seq_len

    def build_sequence_from_db(self, db: Session, child_id: int) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Retrieves, merges, and chronologically sorts recent learning interactions for a given child.
        Returns (interaction_sequence, is_cold_start).
        """
        raw_events: List[Dict[str, Any]] = []

        # 1. Retrieve LearningHistory records
        histories = (
            db.query(LearningHistory)
            .filter(LearningHistory.child_id == child_id)
            .all()
        )
        for h in histories:
            raw_events.append({
                "source": "history",
                "id": h.id,
                "topic_id": h.topic_id or 1,
                "activity_type": h.activity_type or "lesson",
                "difficulty": h.difficulty or "easy",
                "score": float(h.score if h.score is not None else 100.0),
                "completion_status": h.completion_status or "completed",
                "time_spent": int(h.time_spent or 60),
                "timestamp": h.created_at or datetime.utcnow()
            })

        # 2. Retrieve QuizAttempt records
        attempts = (
            db.query(QuizAttempt)
            .filter(QuizAttempt.child_id == child_id)
            .all()
        )
        for a in attempts:
            quiz = db.query(Quiz).filter(Quiz.id == a.quiz_id).first()
            topic_id = quiz.topic_id if quiz and quiz.topic_id else 1
            difficulty = quiz.difficulty if quiz and quiz.difficulty else "easy"

            raw_events.append({
                "source": "quiz_attempt",
                "id": a.id,
                "topic_id": topic_id,
                "activity_type": "quiz",
                "difficulty": difficulty,
                "score": float(a.percentage if a.percentage is not None else 0.0),
                "completion_status": "completed",
                "time_spent": int(a.time_taken or 60),
                "timestamp": a.completed_at or datetime.utcnow()
            })

        # Cold start check
        if not raw_events:
            return [], True

        # 3. Sort chronologically (oldest first, so sequence flows forward in time)
        raw_events.sort(key=lambda x: x["timestamp"])

        # 4. Truncate to most recent MAX_SEQUENCE_LENGTH
        recent_sequence = raw_events[-self.max_seq_len:]

        return recent_sequence, False
