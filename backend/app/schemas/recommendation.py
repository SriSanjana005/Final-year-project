from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RecommendationResponse(BaseModel):
    id: int
    child_id: int
    content_id: int
    content_title: Optional[str] = None
    content_description: Optional[str] = None
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    difficulty: str # alias or value of target_difficulty
    reason: str
    recommendation_type: str = "rule_based"
    status: str = "recommended"
    avg_score: Optional[float] = None
    generated_at: datetime

    class Config:
        from_attributes = True

class RecommendationAdminResponse(BaseModel):
    id: int
    child_id: int
    child_name: Optional[str] = None
    content_id: int
    content_title: Optional[str] = None
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    difficulty: str
    reason: str
    recommendation_type: str = "rule_based"
    status: str = "recommended"
    avg_score: Optional[float] = None
    generated_at: datetime

    class Config:
        from_attributes = True
