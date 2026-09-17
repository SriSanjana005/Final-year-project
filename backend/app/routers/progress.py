from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.child import ChildProfile
from app.models.parent import ParentProfile
from app.models.parent_child import ParentChild
from app.models.quiz import Quiz
from app.models.topic import Topic
from app.models.quiz_attempt import QuizAttempt
from app.models.learning_history import LearningHistory
from app.schemas.progress import (
    ChildProgressSummaryResponse, TopicPerformanceResponse,
    QuizAttemptSummaryResponse, LearningHistoryResponse
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="", tags=["Performance Tracking & Progress"])

def verify_child_access_authorization(child_id: int, current_user: User, db: Session):
    """
    Verifies that current_user is authorized to access child_id data:
    - Child role: user_id must match child_profile.user_id
    - Parent role: parent_profile must be linked to child_id in parent_child_mappings
    - Admin role: full access allowed
    """
    user_role_val = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)

    target_child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not target_child:
        raise HTTPException(status_code=404, detail="Target child profile not found")

    if user_role_val == "admin":
        return target_child

    if user_role_val == "child":
        if target_child.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied: You cannot view another child's progress data")
        return target_child

    if user_role_val == "parent":
        parent_prof = db.query(ParentProfile).filter(ParentProfile.user_id == current_user.id).first()
        if not parent_prof:
            raise HTTPException(status_code=403, detail="Access denied: Parent profile not found")

        mapping = db.query(ParentChild).filter(
            ParentChild.parent_id == parent_prof.id,
            ParentChild.child_id == child_id
        ).first()
        if not mapping:
            raise HTTPException(status_code=403, detail="Access denied: This child is not linked to your parent account")
        return target_child

    raise HTTPException(status_code=403, detail="Operation not permitted")

# GET /api/progress/child/{child_id}
@router.get("/progress/child/{child_id}", response_model=ChildProgressSummaryResponse)
def get_child_progress_summary(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    target_child = verify_child_access_authorization(child_id, current_user, db)

    attempts = db.query(QuizAttempt).filter(QuizAttempt.child_id == child_id).order_by(QuizAttempt.completed_at.desc()).all()
    total_completed = len(attempts)
    
    if total_completed > 0:
        overall_avg = round(sum(a.percentage for a in attempts) / total_completed, 2)
    else:
        overall_avg = 0.0

    # Topic-wise performance calculation
    # Group attempts by topic
    topic_map = {}
    for a in attempts:
        quiz = db.query(Quiz).filter(Quiz.id == a.quiz_id).first()
        if quiz and quiz.topic:
            t_id = quiz.topic.id
            t_name = quiz.topic.name
            if t_id not in topic_map:
                topic_map[t_id] = {"name": t_name, "percentages": []}
            topic_map[t_id]["percentages"].append(a.percentage)

    topic_performances = []
    for t_id, data in topic_map.items():
        avg_p = round(sum(data["percentages"]) / len(data["percentages"]), 2)
        topic_performances.append(TopicPerformanceResponse(
            topic_id=t_id,
            topic_name=data["name"],
            quizzes_taken=len(data["percentages"]),
            average_percentage=avg_p
        ))

    recent_attempts_res = []
    for a in attempts[:10]: # Return last 10 attempts
        quiz = db.query(Quiz).filter(Quiz.id == a.quiz_id).first()
        quiz_title = quiz.title if quiz else "Quiz Assessment"
        topic_name = quiz.topic.name if (quiz and quiz.topic) else "General"

        recent_attempts_res.append(QuizAttemptSummaryResponse(
            attempt_id=a.id,
            quiz_id=a.quiz_id,
            quiz_title=quiz_title,
            topic_name=topic_name,
            difficulty=quiz.difficulty if quiz else "easy",
            score=a.score,
            total_questions=a.total_questions,
            percentage=a.percentage,
            time_taken=a.time_taken,
            completed_at=a.completed_at
        ))

    return ChildProgressSummaryResponse(
        child_id=child_id,
        child_name=target_child.user.name if target_child.user else "Child Learner",
        total_quizzes_completed=total_completed,
        overall_average_percentage=overall_avg,
        topic_performances=topic_performances,
        recent_attempts=recent_attempts_res
    )

# GET /api/history/child/{child_id}
@router.get("/history/child/{child_id}", response_model=List[LearningHistoryResponse])
def get_child_learning_history(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_child_access_authorization(child_id, current_user, db)

    histories = db.query(LearningHistory).filter(LearningHistory.child_id == child_id).order_by(LearningHistory.created_at.desc()).all()
    
    res = []
    for h in histories:
        topic_name = h.topic.name if h.topic else "General"
        res.append(LearningHistoryResponse(
            id=h.id,
            child_id=h.child_id,
            activity_type=h.activity_type,
            activity_id=h.activity_id,
            topic_name=topic_name,
            difficulty=h.difficulty,
            score=h.score,
            completion_status=h.completion_status,
            time_spent=h.time_spent,
            created_at=h.created_at
        ))
    return res
