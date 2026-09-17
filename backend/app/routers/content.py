from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.user import User
from app.models.topic import Topic
from app.models.content import LearningContent
from app.schemas.content import (
    LearningContentCreate, LearningContentUpdate,
    LearningContentResponse, PublishStatusToggle
)
from app.core.dependencies import get_current_user, require_role

router = APIRouter(prefix="/content", tags=["Learning Content Management"])

# GET /api/content/published (Child / Parent / Public)
# CRITICAL SECURITY: Never trust frontend. Must return ONLY published content from active topics.
@router.get("/published", response_model=List[LearningContentResponse])
def get_published_content(
    topic_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    content_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(LearningContent).join(Topic).filter(
        LearningContent.is_published == True,
        Topic.is_active == True
    )

    if topic_id:
        query = query.filter(LearningContent.topic_id == topic_id)
    if difficulty:
        query = query.filter(LearningContent.difficulty == difficulty)
    if content_type:
        query = query.filter(LearningContent.content_type == content_type)

    return query.order_by(LearningContent.created_at.desc()).all()

# GET /api/content (Admin only - returns all content with filters)
@router.get("", response_model=List[LearningContentResponse])
def get_all_content(
    topic_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    content_type: Optional[str] = None,
    is_published: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    query = db.query(LearningContent)

    if topic_id:
        query = query.filter(LearningContent.topic_id == topic_id)
    if difficulty:
        query = query.filter(LearningContent.difficulty == difficulty)
    if content_type:
        query = query.filter(LearningContent.content_type == content_type)
    if is_published is not None:
        query = query.filter(LearningContent.is_published == is_published)
    if search:
        query = query.filter(LearningContent.title.ilike(f"%{search}%"))

    return query.order_by(LearningContent.id.desc()).all()

# GET /api/content/{content_id}
@router.get("/{content_id}", response_model=LearningContentResponse)
def get_content_by_id(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content = db.query(LearningContent).filter(LearningContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Learning content not found")

    user_role_val = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role_val in ["child", "parent"]:
        if not content.is_published or (content.topic and not content.topic.is_active):
            raise HTTPException(status_code=403, detail="Access denied to unpublished educational content")

    return content

# POST /api/content (Admin only)
@router.post("", response_model=LearningContentResponse, status_code=status.HTTP_201_CREATED)
def create_content(
    content_in: LearningContentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    topic = db.query(Topic).filter(Topic.id == content_in.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Selected topic does not exist")

    new_content = LearningContent(
        topic_id=content_in.topic_id,
        title=content_in.title,
        description=content_in.description,
        content_type=content_in.content_type,
        content_body=content_in.content_body,
        difficulty=content_in.difficulty,
        estimated_duration=content_in.estimated_duration,
        is_published=content_in.is_published,
        created_by=current_user.id
    )
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    return new_content

# PUT /api/content/{content_id} (Admin only)
@router.put("/{content_id}", response_model=LearningContentResponse)
def update_content(
    content_id: int,
    content_in: LearningContentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    content = db.query(LearningContent).filter(LearningContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Learning content not found")

    if content_in.topic_id is not None:
        topic = db.query(Topic).filter(Topic.id == content_in.topic_id).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Selected topic does not exist")
        content.topic_id = content_in.topic_id

    if content_in.title is not None:
        content.title = content_in.title
    if content_in.description is not None:
        content.description = content_in.description
    if content_in.content_type is not None:
        content.content_type = content_in.content_type
    if content_in.content_body is not None:
        content.content_body = content_in.content_body
    if content_in.difficulty is not None:
        content.difficulty = content_in.difficulty
    if content_in.estimated_duration is not None:
        content.estimated_duration = content_in.estimated_duration
    if content_in.is_published is not None:
        content.is_published = content_in.is_published

    db.commit()
    db.refresh(content)
    return content

# PATCH /api/content/{content_id}/publish (Admin only)
@router.patch("/{content_id}/publish", response_model=LearningContentResponse)
def toggle_publish_status(
    content_id: int,
    status_in: PublishStatusToggle,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    content = db.query(LearningContent).filter(LearningContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Learning content not found")

    content.is_published = status_in.is_published
    db.commit()
    db.refresh(content)
    return content

# DELETE /api/content/{content_id} (Admin only)
@router.delete("/{content_id}", status_code=status.HTTP_200_OK)
def delete_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    content = db.query(LearningContent).filter(LearningContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Learning content not found")

    db.delete(content)
    db.commit()
    return {"message": "Learning content deleted successfully"}
