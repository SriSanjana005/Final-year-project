from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, List
from app.models.child import ChildProfile
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz import Quiz
from app.models.content import LearningContent
from app.models.topic import Topic
from app.models.learning_history import LearningHistory
from app.models.recommendation import Recommendation

# Configurable recent attempt window size N
RECENT_ATTEMPTS_N = 3

class RecommendationService:
    @staticmethod
    def generate_recommendation(db: Session, child_id: int, N: int = RECENT_ATTEMPTS_N) -> Optional[Recommendation]:
        """
        Generates an explainable rule-based recommendation baseline for a given child.
        """
        # 1. Verify child exists
        child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
        if not child:
            return None

        # 2. Retrieve child's recent completed quiz attempts
        attempts = (
            db.query(QuizAttempt)
            .filter(QuizAttempt.child_id == child_id)
            .order_by(desc(QuizAttempt.completed_at))
            .all()
        )

        # 3. Handle COLD START scenario if child has no quiz history
        if not attempts:
            return RecommendationService._handle_cold_start(db, child_id)

        # 4. Group recent N attempts by topic to find topic needing attention
        topic_attempts_map = {}
        for att in attempts:
            quiz = db.query(Quiz).filter(Quiz.id == att.quiz_id).first()
            if not quiz or not quiz.topic_id:
                continue
            t_id = quiz.topic_id
            if t_id not in topic_attempts_map:
                topic_attempts_map[t_id] = {
                    "topic_id": t_id,
                    "scores": [],
                    "latest_difficulty": quiz.difficulty or "easy",
                    "latest_attempt_time": att.completed_at
                }
            if len(topic_attempts_map[t_id]["scores"]) < N:
                topic_attempts_map[t_id]["scores"].append(att.percentage)


        if not topic_attempts_map:
            return RecommendationService._handle_cold_start(db, child_id)

        # 5. Prioritize topic with lowest recent average score
        sorted_topics = []
        for t_id, t_info in topic_attempts_map.items():
            avg_score = sum(t_info["scores"]) / len(t_info["scores"])
            sorted_topics.append({
                "topic_id": t_id,
                "avg_score": avg_score,
                "latest_difficulty": t_info["latest_difficulty"],
                "latest_attempt_time": t_info["latest_attempt_time"]
            })

        # Sort by avg_score ascending, then by latest_attempt_time descending
        sorted_topics.sort(key=lambda x: (x["avg_score"], -x["latest_attempt_time"].timestamp()))

        selected_topic_info = sorted_topics[0]
        topic_id = selected_topic_info["topic_id"]
        avg_score = selected_topic_info["avg_score"]
        current_difficulty = selected_topic_info["latest_difficulty"]

        # 6. Apply Rule-Based Thresholds
        target_difficulty = current_difficulty
        reason = ""

        if avg_score < 50.0:
            target_difficulty = "easy"
            reason = "Additional practice is recommended based on recent quiz performance."
        elif avg_score < 80.0:
            target_difficulty = current_difficulty
            reason = "Continue practicing this topic to strengthen your understanding."
        else:
            # Score >= 80% -> Recommend higher difficulty if possible
            if current_difficulty == "easy":
                target_difficulty = "medium"
            elif current_difficulty == "medium":
                target_difficulty = "hard"
            else: # hard
                target_difficulty = "hard"
            reason = "Strong recent performance suggests that a higher difficulty level may be appropriate."

        # 7. Content Selection & Repetition Avoidance
        content = RecommendationService._select_content(db, child_id, topic_id, target_difficulty)

        if not content:
            # Fallback to any published content in the system
            content = (
                db.query(LearningContent)
                .filter(LearningContent.is_published == True)
                .first()
            )
            if not content:
                return None
            topic_id = content.topic_id
            target_difficulty = content.difficulty or "easy"
            reason = "Recommended practice content from your curriculum."

        # 8. Store recommendation
        rec = Recommendation(
            child_id=child_id,
            content_id=content.id,
            topic_id=topic_id,
            target_difficulty=target_difficulty,
            reason=reason,
            recommendation_type="rule_based",
            status="recommended",
            avg_score=avg_score
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec

    @staticmethod
    def _handle_cold_start(db: Session, child_id: int) -> Optional[Recommendation]:
        """Cold-start strategy for learners with no performance history."""
        content = (
            db.query(LearningContent)
            .filter(LearningContent.is_published == True)
            .filter(LearningContent.difficulty == "easy")
            .first()
        )
        if not content:
            content = (
                db.query(LearningContent)
                .filter(LearningContent.is_published == True)
                .first()
            )
        if not content:
            return None

        rec = Recommendation(
            child_id=child_id,
            content_id=content.id,
            topic_id=content.topic_id,
            target_difficulty=content.difficulty or "easy",
            reason="Welcome! Here is an introductory learning module to get you started.",
            recommendation_type="rule_based",
            status="recommended",
            avg_score=None
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec

    @staticmethod
    def _select_content(db: Session, child_id: int, topic_id: int, target_difficulty: str) -> Optional[LearningContent]:
        """
        Selects published content for topic and difficulty, avoiding completed repetition.
        """
        # Fetch published candidate contents for topic and difficulty
        candidates = (
            db.query(LearningContent)
            .filter(
                LearningContent.topic_id == topic_id,
                LearningContent.is_published == True,
                LearningContent.difficulty == target_difficulty
            )
            .all()
        )

        # Fallback if no matching difficulty in topic
        if not candidates:
            candidates = (
                db.query(LearningContent)
                .filter(
                    LearningContent.topic_id == topic_id,
                    LearningContent.is_published == True
                )
                .all()
            )


        if not candidates:
            return None

        # Retrieve IDs of content completed by child
        completed_histories = (
            db.query(LearningHistory)
            .filter(LearningHistory.child_id == child_id, LearningHistory.activity_type == "lesson")
            .all()
        )
        completed_content_ids = {h.activity_id for h in completed_histories}

        # Prefer uncompleted candidates
        uncompleted_candidates = [c for c in candidates if c.id not in completed_content_ids]
        if uncompleted_candidates:
            return uncompleted_candidates[0]

        # Otherwise pick the first candidate (or least recently completed)
        return candidates[0]
