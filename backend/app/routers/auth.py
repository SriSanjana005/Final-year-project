from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.child import ChildProfile
from app.models.parent import ParentProfile
from app.models.parent_child import ParentChild
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

def seed_demo_users(db: Session):
    """
    Seed initial development users and profiles if the database is empty.
    Development Password: Password123!
    """
    if db.query(User).count() == 0:
        demo_password_hash = get_password_hash("Password123!")
        demo_users = [
            ("Admin User", "admin@example.com", demo_password_hash, UserRole.ADMIN),
            ("Priya Smith (Parent)", "parent@example.com", demo_password_hash, UserRole.PARENT),
            ("Aishwarya Smith (Child)", "child@example.com", demo_password_hash, UserRole.CHILD),
        ]
        
        created_users = {}
        for name, email, pwd_hash, role in demo_users:
            user = User(
                name=name,
                email=email,
                password_hash=pwd_hash,
                role=role,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            created_users[role] = user

        # Create profiles
        parent_prof = ParentProfile(user_id=created_users[UserRole.PARENT].id, phone="555-0199")
        db.add(parent_prof)

        child_prof = ChildProfile(
            user_id=created_users[UserRole.CHILD].id,
            date_of_birth="2018-05-12",
            learning_level="beginner",
            learning_requirements="Visual counters and auditory cues for tactile learning"
        )
        db.add(child_prof)
        db.commit()

        # Create ParentChild mapping
        mapping = ParentChild(
            parent_id=parent_prof.id,
            child_id=child_prof.id,
            relationship_type="Mother"
        )
        db.add(mapping)
        db.commit()

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        seed_demo_users(db)
    except Exception:
        pass

    user = db.query(User).filter(User.email == request.email).first()
    
    invalid_credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
        headers={"WWW-Authenticate": "Bearer"}
    )

    if not user or not user.is_active:
        raise invalid_credentials_exc

    if not verify_password(request.password, user.password_hash):
        raise invalid_credentials_exc

    role_val = user.role.value if hasattr(user.role, "value") else str(user.role)
    token = create_access_token(subject=user.id, role=role_val)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": role_val,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    role_val = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": role_val,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }
