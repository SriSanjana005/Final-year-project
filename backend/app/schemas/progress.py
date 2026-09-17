from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TopicPerformanceResponse(BaseModel):
    topic_id: int
    topic_name: str
    quizzes_taken: int
    average_percentage: float

class QuizAttemptSummaryResponse(BaseModel):
    attempt_id: int
    quiz_id: int
    quiz_title: str
    topic_name: str
    difficulty: str
    score: float
    total_questions: int
    percentage: float
    time_taken: int
    completed_at: datetime

class ChildProgressSummaryResponse(BaseModel):
    child_id: int
    child_name: str
    total_quizzes_completed: int
    overall_average_percentage: float
    topic_performances: List[TopicPerformanceResponse]
    recent_attempts: List[QuizAttemptSummaryResponse]

class LearningHistoryResponse(BaseModel):
    id: int
    child_id: int
    activity_type: str
    activity_id: int
    topic_name: str
    difficulty: str
    score: Optional[float] = None
    completion_status: str
    time_spent: int
    created_at: datetime

    class Config:
        from_attributes = True
