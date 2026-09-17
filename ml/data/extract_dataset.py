import sys
import os
import json
import csv
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.learning_history import LearningHistory
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz import Quiz
from ml.config.training_config import config

def extract_learner_interactions():
    """
    Extracts chronological learning interaction records from the application database.
    Integrates LearningHistory and QuizAttempt records into a unified dataset.
    """
    db: Session = SessionLocal()
    records = []

    try:
        # 1. Query LearningHistory entries
        histories = db.query(LearningHistory).order_by(LearningHistory.created_at.asc()).all()
        for h in histories:
            records.append({
                "source": "learning_history",
                "record_id": f"lh_{h.id}",
                "child_id": h.child_id,
                "topic_id": h.topic_id or 1,
                "activity_type": h.activity_type or "lesson",
                "difficulty": h.difficulty or "easy",
                "score": float(h.score) if h.score is not None else 0.0,
                "completion_status": h.completion_status or "completed",
                "time_spent": float(h.time_spent) if h.time_spent is not None else 60.0,
                "timestamp": h.created_at.isoformat() if h.created_at else datetime.utcnow().isoformat()
            })

        # 2. Query QuizAttempt entries
        attempts = db.query(QuizAttempt).order_by(QuizAttempt.completed_at.asc()).all()
        for a in attempts:
            quiz = db.query(Quiz).filter(Quiz.id == a.quiz_id).first()
            topic_id = quiz.topic_id if quiz and quiz.topic_id else 1
            difficulty = quiz.difficulty if quiz and quiz.difficulty else "easy"

            records.append({
                "source": "quiz_attempt",
                "record_id": f"qa_{a.id}",
                "child_id": a.child_id,
                "topic_id": topic_id,
                "activity_type": "quiz",
                "difficulty": difficulty,
                "score": float(a.percentage) if a.percentage is not None else 0.0,
                "completion_status": "completed",
                "time_spent": float(a.time_taken) if a.time_taken is not None else 120.0,
                "timestamp": a.completed_at.isoformat() if a.completed_at else datetime.utcnow().isoformat()
            })

    except Exception as e:
        print(f"Notice during DB dataset extraction: {e}")
    finally:
        db.close()

    # 3. Sort chronologically by timestamp
    records.sort(key=lambda x: x["timestamp"])

    # 4. Save to processed directory
    os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
    json_path = os.path.join(config.PROCESSED_DATA_DIR, "learner_interactions.json")
    csv_path = os.path.join(config.PROCESSED_DATA_DIR, "learner_interactions.csv")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    if records:
        fieldnames = list(records[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

    children_represented = len(set(r["child_id"] for r in records))
    topics_represented = len(set(r["topic_id"] for r in records))

    print(f"Extracted {len(records)} total interaction records across {children_represented} children and {topics_represented} topics.")
    print(f"Saved dataset to {json_path}")

    return records

if __name__ == "__main__":
    extract_learner_interactions()
