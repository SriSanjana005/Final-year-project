from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Topic Schemas
class TopicBase(BaseModel):
    name: str
    subject: str
    description: Optional[str] = None
    is_active: bool = True

class TopicCreate(TopicBase):
    pass

class TopicUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class TopicResponse(TopicBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Learning Content Schemas
class LearningContentBase(BaseModel):
    topic_id: int
    title: str
    description: Optional[str] = None
    content_type: str = "lesson" # lesson, video, practice, activity
    content_body: str
    difficulty: str = "easy" # easy, medium, hard
    estimated_duration: int = 10
    is_published: bool = False

class LearningContentCreate(LearningContentBase):
    pass

class LearningContentUpdate(BaseModel):
    topic_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[str] = None
    content_body: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_duration: Optional[int] = None
    is_published: Optional[bool] = None

class LearningContentResponse(LearningContentBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    topic: Optional[TopicResponse] = None

    class Config:
        from_attributes = True

class PublishStatusToggle(BaseModel):
    is_published: bool
