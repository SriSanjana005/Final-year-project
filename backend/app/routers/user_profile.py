from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.child import ChildProfile
from app.models.parent import ParentProfile
from app.models.parent_child import ParentChild
from app.core.security import get_password_hash
from app.schemas.user_profile import (
    UserBase, UserCreate, UserResponse, ChildProfileResponse, ParentProfileResponse,
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

# POST /api/users (Admin only)
@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    role_val = payload.role.lower().strip()
    if role_val == "child":
        role_enum = UserRole.CHILD
    elif role_val == "parent":
        role_enum = UserRole.PARENT
    elif role_val == "admin":
        role_enum = UserRole.ADMIN
    else:
        raise HTTPException(status_code=400, detail=f"Invalid user role: {payload.role}")

    pwd_hash = get_password_hash(payload.password)

    new_user = User(
        name=payload.name,
        email=payload.email,
        password_hash=pwd_hash,
        role=role_enum,
        is_active=True,
        is_test_data=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    if role_enum == UserRole.CHILD:
        child_prof = ChildProfile(
            user_id=new_user.id,
            date_of_birth=payload.date_of_birth or "2018-01-01",
            learning_level=payload.learning_level or "beginner"
        )
        db.add(child_prof)
        db.commit()
    elif role_enum == UserRole.PARENT:
        parent_prof = ParentProfile(
            user_id=new_user.id,
            phone=payload.phone or "555-0100"
        )
        db.add(parent_prof)
        db.commit()

    return new_user

# DELETE /api/users/{user_id} (Admin only)
@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own admin account")

    db.delete(target_user)
    db.commit()
    return {"message": "User deleted successfully"}

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
