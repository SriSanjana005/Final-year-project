from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    full_name: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Login Request
class LoginRequest(BaseModel):
    email: str
    password: str

# Health Check Response
class HealthResponse(BaseModel):
    status: str
    database: str
    version: str = "1.0.0"

# Topic Schemas
class TopicBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    icon_name: Optional[str] = "book"

class TopicCreate(TopicBase):
    pass

class TopicResponse(TopicBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Learning Content Schemas
class LearningContentBase(BaseModel):
    topic_id: int
    title: str
    content_body: str
    media_url: Optional[str] = None
    difficulty_level: int = 1
    estimated_minutes: int = 5

class LearningContentCreate(LearningContentBase):
    pass

class LearningContentResponse(LearningContentBase):
    id: int
    is_approved: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Quiz & Question Schemas
class QuestionBase(BaseModel):
    question_text: str
    options: List[str]
    correct_option_index: int
    explanation: Optional[str] = None
    difficulty_level: int = 1

class QuestionResponse(QuestionBase):
    id: int
    quiz_id: int

    class Config:
        from_attributes = True

class QuizBase(BaseModel):
    topic_id: int
    title: str
    description: Optional[str] = None
    passing_percentage: int = 70

class QuizResponse(QuizBase):
    id: int
    created_at: datetime
    questions: List[QuestionResponse] = []

    class Config:
        from_attributes = True

# Quiz Attempt Schema
class QuizAttemptCreate(BaseModel):
    quiz_id: int
    score: float
    total_questions: int
    time_spent_seconds: int

class QuizAttemptResponse(QuizAttemptCreate):
    id: int
    child_id: int
    passed: bool
    completed_at: datetime

    class Config:
        from_attributes = True

# Progress & Recommendation Schemas
class ChildProgressSummary(BaseModel):
    child_id: int
    child_name: str
    overall_progress_percentage: float
    completed_topics_count: int
    total_quizzes_taken: int
    average_quiz_score: float
    current_learning_streak_days: int

class RecommendationResponse(BaseModel):
    id: int
    child_id: int
    content_id: int
    content_title: str
    recommended_by: str
    action_type: str
    confidence_score: float
    is_completed: bool

    class Config:
        from_attributes = True
