from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.child import ChildProfile
from app.models.parent import ParentProfile
from app.models.parent_child import ParentChild
from app.models.recommendation import Recommendation
from app.models.content import LearningContent
from app.models.topic import Topic
from app.schemas.recommendation import RecommendationResponse, RecommendationAdminResponse
from app.services.recommendation_service import RecommendationService
from app.services.ai_availability_service import AIAvailabilityService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

def verify_child_access(db: Session, current_user: User, child_id: int):
    """Enforces role-based authorization for child data access."""
    if current_user.role == UserRole.ADMIN:
        return
    if current_user.role == UserRole.CHILD:
        child_profile = db.query(ChildProfile).filter(ChildProfile.user_id == current_user.id).first()
        if not child_profile or child_profile.id != child_id:
            raise HTTPException(status_code=403, detail="Access denied: You can only view your own recommendations.")
        return
    if current_user.role == UserRole.PARENT:
        parent_profile = db.query(ParentProfile).filter(ParentProfile.user_id == current_user.id).first()
        if not parent_profile:
            raise HTTPException(status_code=403, detail="Parent profile not found.")
        link = db.query(ParentChild).filter(
            ParentChild.parent_id == parent_profile.id,
            ParentChild.child_id == child_id
        ).first()
        if not link:
            raise HTTPException(status_code=403, detail="Access denied: Learner is not linked to your parent account.")
        return
    raise HTTPException(status_code=403, detail="Access denied.")

def format_recommendation_response(db: Session, rec: Recommendation) -> dict:
    content = db.query(LearningContent).filter(LearningContent.id == rec.content_id).first()
    topic = db.query(Topic).filter(Topic.id == rec.topic_id).first() if rec.topic_id else None
    return {
        "id": rec.id,
        "child_id": rec.child_id,
        "content_id": rec.content_id,
        "content_title": content.title if content else "Recommended Module",
        "content_description": content.description if content else None,
        "topic_id": rec.topic_id,
        "topic_name": topic.name if topic else (content.topic.name if content and content.topic else "General"),
        "difficulty": rec.target_difficulty,
        "reason": rec.reason,
        "recommendation_type": rec.recommendation_type,
        "status": rec.status,
        "avg_score": rec.avg_score,
        "generated_at": rec.generated_at
    }

@router.get("/ai-status")
def get_ai_status(
    child_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns system-wide or child-specific AI availability metrics, cold-start status,
    and recommendation strategy selection.
    """
    if current_user.role == UserRole.CHILD:
        child_profile = db.query(ChildProfile).filter(ChildProfile.user_id == current_user.id).first()
        target_child_id = child_profile.id if child_profile else 1
    elif child_id:
        verify_child_access(db, current_user, child_id)
        target_child_id = child_id
    else:
        target_child_id = 1

    return AIAvailabilityService.check_ai_status(db, target_child_id)

@router.get("/current", response_model=RecommendationResponse)
def get_current_recommendation(
    child_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns the current active recommendation for the learner.
    Does NOT generate duplicate recommendation records unnecessarily if an active ('recommended' or 'viewed') recommendation exists.
    """
    if current_user.role == UserRole.CHILD:
        child_profile = db.query(ChildProfile).filter(ChildProfile.user_id == current_user.id).first()
        if not child_profile:
            raise HTTPException(status_code=404, detail="Child profile not found.")
        target_child_id = child_profile.id
    else:
        if not child_id:
            raise HTTPException(status_code=400, detail="child_id parameter is required for parents and admins.")
        verify_child_access(db, current_user, child_id)
        target_child_id = child_id

    # Fetch active recommended or viewed recommendation
    rec = (
        db.query(Recommendation)
        .filter(
            Recommendation.child_id == target_child_id,
            Recommendation.status.in_(["recommended", "viewed"])
        )
        .order_by(Recommendation.generated_at.desc())
        .first()
    )

    if not rec:
        rec = RecommendationService.generate_recommendation(db, target_child_id)
        if not rec:
            raise HTTPException(status_code=404, detail="No suitable content available for recommendation.")

    return format_recommendation_response(db, rec)

@router.get("", response_model=List[RecommendationResponse])
def get_recommendations(
    child_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns list of recommendations for the authenticated child or parent's child."""
    if current_user.role == UserRole.CHILD:
        child_profile = db.query(ChildProfile).filter(ChildProfile.user_id == current_user.id).first()
        if not child_profile:
            raise HTTPException(status_code=404, detail="Child profile not found.")
        target_child_id = child_profile.id
    else:
        if not child_id:
            raise HTTPException(status_code=400, detail="child_id parameter is required.")
        verify_child_access(db, current_user, child_id)
        target_child_id = child_id

    recs = (
        db.query(Recommendation)
        .filter(Recommendation.child_id == target_child_id)
        .order_by(Recommendation.generated_at.desc())
        .all()
    )

    return [format_recommendation_response(db, r) for r in recs]

@router.post("/generate", response_model=RecommendationResponse)
def generate_recommendation_endpoint(
    child_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generates a new personalized recommendation based on active Strategy configuration."""
    if current_user.role == UserRole.CHILD:
        child_profile = db.query(ChildProfile).filter(ChildProfile.user_id == current_user.id).first()
        target_child_id = child_profile.id
    else:
        if not child_id:
            raise HTTPException(status_code=400, detail="child_id is required.")
        verify_child_access(db, current_user, child_id)
        target_child_id = child_id

    rec = RecommendationService.generate_recommendation(db, target_child_id)
    if not rec:
        raise HTTPException(status_code=400, detail="Unable to generate recommendation.")

    return format_recommendation_response(db, rec)

@router.post("/{recommendation_id}/view", response_model=RecommendationResponse)
def mark_recommendation_viewed(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marks recommendation status as viewed."""
    rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found.")

    verify_child_access(db, current_user, rec.child_id)
    rec.status = "viewed"
    db.commit()
    db.refresh(rec)
    return format_recommendation_response(db, rec)

@router.post("/{recommendation_id}/complete", response_model=RecommendationResponse)
def mark_recommendation_completed(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marks recommendation status as completed upon finishing recommended activity."""
    rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found.")

    verify_child_access(db, current_user, rec.child_id)
    rec.status = "completed"
    db.commit()
    db.refresh(rec)
    return format_recommendation_response(db, rec)

@router.get("/admin/all", response_model=List[RecommendationAdminResponse])
def get_all_recommendations_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin monitoring endpoint to view all recommendation logs across all learners."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin authorization required.")

    recs = db.query(Recommendation).order_by(Recommendation.generated_at.desc()).all()
    results = []
    for r in recs:
        child = db.query(ChildProfile).filter(ChildProfile.id == r.child_id).first()
        child_name = child.user.name if child and child.user else f"Child #{r.child_id}"
        content = db.query(LearningContent).filter(LearningContent.id == r.content_id).first()
        topic = db.query(Topic).filter(Topic.id == r.topic_id).first() if r.topic_id else None

        results.append({
            "id": r.id,
            "child_id": r.child_id,
            "child_name": child_name,
            "content_id": r.content_id,
            "content_title": content.title if content else "Recommended Module",
            "topic_id": r.topic_id,
            "topic_name": topic.name if topic else (content.topic.name if content and content.topic else "General"),
            "difficulty": r.target_difficulty,
            "reason": r.reason,
            "recommendation_type": r.recommendation_type,
            "status": r.status,
            "avg_score": r.avg_score,
            "generated_at": r.generated_at
        })
    return results

@router.get("/admin/evaluation/summary")
def get_admin_evaluation_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin-only endpoint returning experimental evaluation summary,
    baseline vs proposed strategy comparison, content safety audit, and model metrics.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin authorization required.")

    try:
        from ml.evaluation.evaluator import run_evaluation_pipeline
        summary = run_evaluation_pipeline(db)
        return summary
    except Exception as e:
        print(f"Evaluation summary pipeline notice: {e}")
        return {
            "evaluation_status": "insufficient_data",
            "message": str(e)
        }
