from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.child import ChildProfile
from app.models.parent import ParentProfile
from app.models.parent_child import ParentChild
from app.models.topic import Topic
from app.models.content import LearningContent
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

def seed_demo_users(db: Session):
    """
    Seed initial development users, profiles, topics, and sample educational content.
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

        # Create Seed Topics
        t_addition = Topic(name="Addition", subject="Mathematics", description="Learn single and double digit addition with visual blocks.", is_active=True)
        t_subtraction = Topic(name="Subtraction", subject="Mathematics", description="Basic subtraction concepts and visual takeaway counters.", is_active=True)
        t_vocab = Topic(name="Vocabulary", subject="English", description="Sight words, object matching, and picture cards.", is_active=True)
        t_animals = Topic(name="Animals", subject="Science", description="Discover animals, their sounds, and natural habitats.", is_active=True)
        
        db.add_all([t_addition, t_subtraction, t_vocab, t_animals])
        db.commit()

        # Create Seed Educational Content
        admin_id = created_users[UserRole.ADMIN].id
        c1 = LearningContent(
            topic_id=t_addition.id,
            title="Introduction to Addition",
            description="Learn how to combine groups of objects using visual counters.",
            content_type="lesson",
            content_body="Welcome to Addition! Addition means putting groups together. When you have 3 blocks and add 2 more blocks, you get 5 blocks in total. 🟦 🟦 🟦 + 🟦 🟦 = 🟦 🟦 🟦 🟦 🟦. Practice counting out loud!",
            difficulty="easy",
            estimated_duration=10,
            is_published=True,
            created_by=admin_id
        )
        c2 = LearningContent(
            topic_id=t_addition.id,
            title="Addition Practice with Blocks",
            description="Interactive exercise combining 2-digit numbers.",
            content_type="practice",
            content_body="Count the visual groups carefully: Group A has 4 green circles, Group B has 3 yellow circles. How many circles are there altogether?",
            difficulty="medium",
            estimated_duration=15,
            is_published=True,
            created_by=admin_id
        )
        c3 = LearningContent(
            topic_id=t_vocab.id,
            title="Sight Words & Object Matching",
            description="Match words with tactile visual pictures.",
            content_type="activity",
            content_body="Look at the word: CAT 🐱. Look at the word: DOG 🐶. Look at the word: SUN ☀️. Point to each word as you say it out loud.",
            difficulty="easy",
            estimated_duration=8,
            is_published=True,
            created_by=admin_id
        )
        c4 = LearningContent(
            topic_id=t_subtraction.id,
            title="Basic Subtraction Concepts (Draft)",
            description="Understanding taking away objects from a set.",
            content_type="lesson",
            content_body="Subtraction means taking away! If you have 5 apples and eat 2, you have 3 apples left.",
            difficulty="easy",
            estimated_duration=10,
            is_published=False, # Unpublished draft for admin testing
            created_by=admin_id
        )

        db.add_all([c1, c2, c3, c4])
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
