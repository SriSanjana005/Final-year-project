import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from app.models.child import ChildProfile
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz import Quiz
from app.models.content import LearningContent
from app.models.topic import Topic
from app.models.learning_history import LearningHistory
from app.models.recommendation import Recommendation

logger = logging.getLogger(__name__)

# Configurable recent attempt window size N
RECENT_ATTEMPTS_N = 3

class RecommendationService:
    @staticmethod
    def generate_recommendation(db: Session, child_id: int) -> Optional[Recommendation]:
        """
        Primary entry point for recommendation generation.
        Delegates to AIRecommendationService which handles Strategy selection (AUTO, TRANSFORMER_PPO, RULE_BASED),
        cold-start evaluation, and safe fallback.
        """
        from app.services.ai_recommendation_service import AIRecommendationService
        return AIRecommendationService.generate_personalized_recommendation(db, child_id)

    @staticmethod
    def generate_rule_based_recommendation(db: Session, child_id: int, N: int = RECENT_ATTEMPTS_N) -> Optional[Recommendation]:
        """
        Rule-Based Baseline Strategy implementation.
        Evaluates learner's recent quiz performance history by topic and selects appropriate difficulty content.
        Used for cold-start and fallback scenarios.
        """
        child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
        if not child:
            logger.warning(f"Child profile #{child_id} not found for rule-based recommendation.")
            return None

        # 1. Retrieve recent completed quiz attempts
        attempts = (
            db.query(QuizAttempt)
            .filter(QuizAttempt.child_id == child_id)
            .order_by(desc(QuizAttempt.completed_at))
            .all()
        )

        # 2. COLD START handling if child has no quiz history
        if not attempts:
            return RecommendationService._handle_cold_start(db, child_id)

        # 3. Group recent N attempts by topic to identify topic needing attention
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

        # 4. Prioritize topic with lowest recent average score
        sorted_topics = []
        for t_id, t_info in topic_attempts_map.items():
            avg_score = sum(t_info["scores"]) / len(t_info["scores"])
            sorted_topics.append({
                "topic_id": t_id,
                "avg_score": avg_score,
                "latest_difficulty": t_info["latest_difficulty"],
                "latest_attempt_time": t_info["latest_attempt_time"]
            })

        sorted_topics.sort(key=lambda x: (x["avg_score"], -x["latest_attempt_time"].timestamp()))

        selected_topic_info = sorted_topics[0]
        topic_id = selected_topic_info["topic_id"]
        avg_score = selected_topic_info["avg_score"]
        current_difficulty = selected_topic_info["latest_difficulty"]

        # 5. Apply Rule-Based Threshold Rules
        if avg_score < 50.0:
            target_difficulty = "easy"
            reason = "Additional practice is recommended based on recent quiz performance."
        elif avg_score < 80.0:
            target_difficulty = current_difficulty
            reason = "Continue practicing this topic to strengthen your understanding."
        else:
            if current_difficulty == "easy":
                target_difficulty = "medium"
            elif current_difficulty == "medium":
                target_difficulty = "hard"
            else:
                target_difficulty = "hard"
            reason = "Strong recent performance suggests that a higher difficulty level may be appropriate."

        # 6. Content Selection & Repetition Avoidance
        content = RecommendationService._select_content(db, child_id, topic_id, target_difficulty)

        if not content:
            content = (
                db.query(LearningContent)
                .filter(LearningContent.is_published == True)
                .first()
            )
            if not content:
                logger.error("No published content found in system for rule-based recommendation fallback.")
                return None
            topic_id = content.topic_id
            target_difficulty = content.difficulty or "easy"
            reason = "Recommended practice content from your curriculum."

        # 7. Store Rule-Based Recommendation Record
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
        logger.info(f"Created rule-based recommendation #{rec.id} for child #{child_id}")
        return rec

    @staticmethod
    def _handle_cold_start(db: Session, child_id: int) -> Optional[Recommendation]:
        """Cold-start strategy for learners with no performance history."""
        content = (
            db.query(LearningContent)
            .filter(LearningContent.is_published == True, LearningContent.difficulty == "easy")
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
        logger.info(f"Created cold-start recommendation #{rec.id} for child #{child_id}")
        return rec

    @staticmethod
    def _select_content(db: Session, child_id: int, topic_id: int, target_difficulty: str) -> Optional[LearningContent]:
        """Selects published content for topic and difficulty, avoiding completed repetition."""
        candidates = (
            db.query(LearningContent)
            .filter(
                LearningContent.topic_id == topic_id,
                LearningContent.is_published == True,
                LearningContent.difficulty == target_difficulty
            )
            .all()
        )

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

        completed_histories = (
            db.query(LearningHistory)
            .filter(LearningHistory.child_id == child_id, LearningHistory.activity_type == "lesson")
            .all()
        )
        completed_content_ids = {h.activity_id for h in completed_histories}

        uncompleted_candidates = [c for c in candidates if c.id not in completed_content_ids]
        if uncompleted_candidates:
            return uncompleted_candidates[0]

        return candidates[0]
