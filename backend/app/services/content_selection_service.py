import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from app.models.content import LearningContent
from app.models.learning_history import LearningHistory
from app.models.recommendation import Recommendation
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz import Quiz
from ml.reinforcement_learning.actions import ActionType

logger = logging.getLogger(__name__)

class ContentSelectionService:
    @staticmethod
    def select_content_for_action(
        db: Session,
        child_id: int,
        action_type: ActionType,
        current_topic_id: Optional[int] = None,
        current_difficulty: str = "easy"
    ) -> Optional[LearningContent]:
        """
        Selects an admin-approved, published LearningContent matching the given PPO action criteria
        while enforcing content approval boundaries and avoiding recent repetitions.
        """
        # 1. Retrieve completed & recently recommended content IDs to avoid repetition
        completed_histories = (
            db.query(LearningHistory)
            .filter(LearningHistory.child_id == child_id)
            .all()
        )
        completed_content_ids = {h.activity_id for h in completed_histories if h.activity_type == "lesson"}

        recent_recs = (
            db.query(Recommendation)
            .filter(Recommendation.child_id == child_id)
            .order_by(desc(Recommendation.generated_at))
            .limit(5)
            .all()
        )
        recently_recommended_ids = {r.content_id for r in recent_recs}

        # Base query: STABLE CONTENT BOUNDARY — strictly published admin content
        base_query = db.query(LearningContent).filter(LearningContent.is_published == True)

        candidates: List[LearningContent] = []

        # 2. Map discrete PPO action to target search criteria
        if action_type == ActionType.REVIEW_PREVIOUS_TOPIC:
            # Query recently completed quiz attempts to find previous topic
            previous_attempts = (
                db.query(QuizAttempt)
                .filter(QuizAttempt.child_id == child_id)
                .order_by(desc(QuizAttempt.completed_at))
                .all()
            )
            previous_topic_id = None
            for att in previous_attempts:
                quiz = db.query(Quiz).filter(Quiz.id == att.quiz_id).first()
                if quiz and quiz.topic_id and quiz.topic_id != current_topic_id:
                    previous_topic_id = quiz.topic_id
                    break

            if previous_topic_id:
                candidates = base_query.filter(LearningContent.topic_id == previous_topic_id).all()
            else:
                # Fallback to easy content in current topic
                if current_topic_id:
                    candidates = base_query.filter(
                        LearningContent.topic_id == current_topic_id,
                        LearningContent.difficulty == "easy"
                    ).all()

        elif action_type == ActionType.EASIER_CONTENT:
            target_diff = "easy"
            if current_topic_id:
                candidates = base_query.filter(
                    LearningContent.topic_id == current_topic_id,
                    LearningContent.difficulty == target_diff
                ).all()
            if not candidates:
                candidates = base_query.filter(LearningContent.difficulty == target_diff).all()

        elif action_type == ActionType.SAME_DIFFICULTY:
            target_diff = current_difficulty
            if current_topic_id:
                candidates = base_query.filter(
                    LearningContent.topic_id == current_topic_id,
                    LearningContent.difficulty == target_diff
                ).all()
            if not candidates:
                candidates = base_query.filter(LearningContent.difficulty == target_diff).all()

        elif action_type == ActionType.HARDER_CONTENT:
            target_diff = "medium" if current_difficulty == "easy" else "hard"
            if current_topic_id:
                candidates = base_query.filter(
                    LearningContent.topic_id == current_topic_id,
                    LearningContent.difficulty == target_diff
                ).all()
            if not candidates:
                candidates = base_query.filter(LearningContent.difficulty == target_diff).all()

        elif action_type == ActionType.PRACTICE_CONTENT:
            if current_topic_id:
                candidates = base_query.filter(
                    LearningContent.topic_id == current_topic_id,
                    LearningContent.content_type == "practice"
                ).all()
            if not candidates:
                candidates = base_query.filter(LearningContent.content_type == "practice").all()

        # Fallback query if candidate list is empty
        if not candidates:
            if current_topic_id:
                candidates = base_query.filter(LearningContent.topic_id == current_topic_id).all()
            if not candidates:
                candidates = base_query.all()

        if not candidates:
            logger.warning(f"No published content available for child #{child_id} with action {action_type}.")
            return None

        # 3. Apply Repetition Avoidance Hierarchy
        # Priority 1: Uncompleted AND not recently recommended
        fresh_candidates = [
            c for c in candidates 
            if c.id not in completed_content_ids and c.id not in recently_recommended_ids
        ]
        if fresh_candidates:
            return fresh_candidates[0]

        # Priority 2: Uncompleted (even if recently recommended)
        uncompleted_candidates = [c for c in candidates if c.id not in completed_content_ids]
        if uncompleted_candidates:
            return uncompleted_candidates[0]

        # Priority 3: Fall back to published candidate content (oldest recommendation or first available)
        logger.info(f"All suitable candidate contents completed by child #{child_id}; re-recommending published content.")
        return candidates[0]
