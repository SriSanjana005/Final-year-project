from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.child import ChildProfile
from app.models.parent import ParentProfile
from app.models.parent_child import ParentChild
from app.services.transformer_service import TransformerService

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

def verify_child_access(db: Session, current_user: User, child_id: int):
    """Enforces strict role authorization for learner state ML metadata."""
    if current_user.role == UserRole.ADMIN:
        return
    if current_user.role == UserRole.CHILD:
        child_profile = db.query(ChildProfile).filter(ChildProfile.user_id == current_user.id).first()
        if not child_profile or child_profile.id != child_id:
            raise HTTPException(status_code=403, detail="Access denied: You can only view your own learner state.")
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

@router.get("/learner-state")
def get_learner_state(
    child_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns Transformer 64-dimensional learner state representation metadata.
    Enforces child/parent role authorization.
    """
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

    result = TransformerService.get_learner_state(db, target_child_id)
    if result.get("model_status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))

    return result
