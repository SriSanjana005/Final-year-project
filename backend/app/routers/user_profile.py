from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.child import ChildProfile
from app.models.parent import ParentProfile
from app.models.parent_child import ParentChild
from app.schemas.user_profile import (
    UserResponse, ChildProfileResponse, ParentProfileResponse,
    ParentChildResponse, AdminMetricsResponse
)
from app.core.dependencies import get_current_user, require_role

router = APIRouter(prefix="", tags=["User Profiles & Mappings"])

# 1. GET /api/users/me
@router.get("/users/me", response_model=UserResponse)
def get_user_me(current_user: User = Depends(get_current_user)):
    return current_user

# 2. GET /api/children/me (Only for child role)
@router.get("/children/me", response_model=ChildProfileResponse)
def get_child_me(current_user: User = Depends(require_role(["child"])), db: Session = Depends(get_db)):
    profile = db.query(ChildProfile).filter(ChildProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Child profile not found")
    return profile

# 3. GET /api/parents/me (Only for parent role)
@router.get("/parents/me", response_model=ParentProfileResponse)
def get_parent_me(current_user: User = Depends(require_role(["parent"])), db: Session = Depends(get_db)):
    profile = db.query(ParentProfile).filter(ParentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Parent profile not found")
    return profile

# 4. GET /api/parents/me/children (Parent can only access their linked children)
@router.get("/parents/me/children", response_model=List[ChildProfileResponse])
def get_my_linked_children(current_user: User = Depends(require_role(["parent"])), db: Session = Depends(get_db)):
    parent_profile = db.query(ParentProfile).filter(ParentProfile.user_id == current_user.id).first()
    if not parent_profile:
        return []
    
    mappings = db.query(ParentChild).filter(ParentChild.parent_id == parent_profile.id).all()
    child_ids = [m.child_id for m in mappings]
    
    children = db.query(ChildProfile).filter(ChildProfile.id.in_(child_ids)).all() if child_ids else []
    return children

# --- ADMIN ENDPOINTS ---

# GET /api/users (Admin only)
@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin"]))):
    return db.query(User).order_by(User.id.asc()).all()

# GET /api/children (Admin only)
@router.get("/children", response_model=List[ChildProfileResponse])
def get_all_children(db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin"]))):
    return db.query(ChildProfile).all()

# GET /api/parents (Admin only)
@router.get("/parents", response_model=List[ParentProfileResponse])
def get_all_parents(db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin"]))):
    return db.query(ParentProfile).all()

# GET /api/admin/metrics (Admin dashboard counts)
@router.get("/admin/metrics", response_model=AdminMetricsResponse)
def get_admin_metrics(db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin"]))):
    return {
        "total_users": db.query(User).count(),
        "total_children": db.query(ChildProfile).count(),
        "total_parents": db.query(ParentProfile).count(),
        "total_mappings": db.query(ParentChild).count()
    }
