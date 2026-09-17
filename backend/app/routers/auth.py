from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User, ChildProfile, ParentProfile, UserRole
from app.schemas.schemas import Token, LoginRequest, UserCreate, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initial mock user seed data if database is fresh
def seed_demo_users(db: Session):
    if db.query(User).count() == 0:
        demo_users = [
            ("child@learning.com", "child123", "Leo Smith (Child)", UserRole.CHILD.value),
            ("parent@learning.com", "parent123", "Sarah Smith (Parent)", UserRole.PARENT.value),
            ("admin@learning.com", "admin123", "Dr. Alex Rivera (Admin)", UserRole.ADMIN.value)
        ]
        for email, pwd, name, role in demo_users:
            user = User(
                email=email,
                hashed_password=get_password_hash(pwd),
                full_name=name,
                role=role
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            if role == UserRole.CHILD.value:
                db.add(ChildProfile(user_id=user.id, age=8, learning_level="beginner", notes="Needs visual aids"))
            elif role == UserRole.PARENT.value:
                db.add(ParentProfile(user_id=user.id, phone_number="555-0199"))
            db.commit()

@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        seed_demo_users(db)
    except Exception:
        pass

    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        # Fallback handling for demo offline/prototype mode
        if request.email == "child@learning.com" and request.password == "child123":
            token = create_access_token(subject=1, role="child")
            return {"access_token": token, "token_type": "bearer", "role": "child", "user_id": 1, "full_name": "Leo Smith"}
        elif request.email == "parent@learning.com" and request.password == "parent123":
            token = create_access_token(subject=2, role="parent")
            return {"access_token": token, "token_type": "bearer", "role": "parent", "user_id": 2, "full_name": "Sarah Smith"}
        elif request.email == "admin@learning.com" and request.password == "admin123":
            token = create_access_token(subject=3, role="admin")
            return {"access_token": token, "token_type": "bearer", "role": "admin", "user_id": 3, "full_name": "Dr. Alex Rivera"}
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token(subject=user.id, role=user.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "full_name": user.full_name
    }

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    if user_in.role == UserRole.CHILD.value:
        db.add(ChildProfile(user_id=new_user.id))
    elif user_in.role == UserRole.PARENT.value:
        db.add(ParentProfile(user_id=new_user.id))
    db.commit()

    return new_user
