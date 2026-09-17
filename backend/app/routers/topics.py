from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.user import User
from app.models.topic import Topic
from app.schemas.content import TopicCreate, TopicUpdate, TopicResponse
from app.core.dependencies import get_current_user, require_role

router = APIRouter(prefix="/topics", tags=["Topic Management"])

# GET /api/topics/active (Child / Parent / Public)
@router.get("/active", response_model=List[TopicResponse])
def get_active_topics(db: Session = Depends(get_db)):
    return db.query(Topic).filter(Topic.is_active == True).order_by(Topic.subject.asc(), Topic.name.asc()).all()

# GET /api/topics (Admin gets all, others get active only)
@router.get("", response_model=List[TopicResponse])
def get_topics(
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_role_val = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role_val != "admin" or active_only:
        return db.query(Topic).filter(Topic.is_active == True).order_by(Topic.subject.asc(), Topic.name.asc()).all()
    return db.query(Topic).order_by(Topic.id.desc()).all()

# GET /api/topics/{topic_id}
@router.get("/{topic_id}", response_model=TopicResponse)
def get_topic_by_id(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

# POST /api/topics (Admin only)
@router.post("", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
def create_topic(
    topic_in: TopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    new_topic = Topic(
        name=topic_in.name,
        subject=topic_in.subject,
        description=topic_in.description,
        is_active=topic_in.is_active
    )
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    return new_topic

# PUT /api/topics/{topic_id} (Admin only)
@router.put("/{topic_id}", response_model=TopicResponse)
def update_topic(
    topic_id: int,
    topic_in: TopicUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    if topic_in.name is not None:
        topic.name = topic_in.name
    if topic_in.subject is not None:
        topic.subject = topic_in.subject
    if topic_in.description is not None:
        topic.description = topic_in.description
    if topic_in.is_active is not None:
        topic.is_active = topic_in.is_active

    db.commit()
    db.refresh(topic)
    return topic

# DELETE /api/topics/{topic_id} (Admin only)
@router.delete("/{topic_id}", status_code=status.HTTP_200_OK)
def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    db.delete(topic)
    db.commit()
    return {"message": "Topic deleted successfully"}
