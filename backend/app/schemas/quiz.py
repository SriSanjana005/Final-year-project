from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.content import TopicResponse

# --- QUESTION SCHEMAS ---
class QuestionBase(BaseModel):
    question_text: str
    question_type: str = "multiple_choice"
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str # A, B, C, D
    explanation: Optional[str] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None

class QuestionResponse(QuestionBase):
    id: int
    quiz_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Child delivery question schema - NEVER expose correct_answer or explanation
class ChildQuestionResponse(BaseModel):
    id: int
    quiz_id: int
    question_text: str
    question_type: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

    class Config:
        from_attributes = True

# --- QUIZ SCHEMAS ---
class QuizBase(BaseModel):
    topic_id: int
    title: str
    description: Optional[str] = None
    difficulty: str = "easy" # easy, medium, hard
    is_published: bool = False

class QuizCreate(QuizBase):
    pass

class QuizUpdate(BaseModel):
    topic_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    is_published: Optional[bool] = None

class QuizResponse(QuizBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    topic: Optional[TopicResponse] = None
    question_count: int = 0

    class Config:
        from_attributes = True

class QuizPublishToggle(BaseModel):
    is_published: bool

# Child quiz attempt package (Quiz info + questions without answers)
class ChildQuizAttemptResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    difficulty: str
    topic_name: str
    questions: List[ChildQuestionResponse]

# --- SUBMISSION SCHEMAS ---
class SingleAnswerSubmission(BaseModel):
    question_id: int
    selected_answer: str # A, B, C, D

class QuizSubmissionRequest(BaseModel):
    time_taken: int = 0 # seconds
    answers: List[SingleAnswerSubmission]

class QuizSubmissionResponse(BaseModel):
    attempt_id: int
    quiz_id: int
    score: float
    total_questions: int
    correct_answers: int
    percentage: float
    time_taken: int
    completed_at: datetime
    performance: str # excellent, good, needs_practice
