from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
from app.models.user import User, UserRole
from app.models.child import ChildProfile
from app.models.parent import ParentProfile
from app.models.parent_child import ParentChild
from app.models.topic import Topic
from app.models.content import LearningContent

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    passing_percentage = Column(Integer, default=70)
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_option_index = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)
    difficulty_level = Column(Integer, default=1)

    quiz = relationship("Quiz", back_populates="questions")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    score = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    time_spent_seconds = Column(Integer, default=0)
    passed = Column(Boolean, default=False)
    completed_at = Column(DateTime, default=datetime.utcnow)

    child = relationship("ChildProfile", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")

class LearningHistory(Base):
    __tablename__ = "learning_histories"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False)
    content_id = Column(Integer, ForeignKey("learning_contents.id"), nullable=True)
    topic_title = Column(String(255), nullable=False)
    difficulty_level = Column(Integer, default=1)
    activity_type = Column(String(50), default="content_read")
    score = Column(Float, nullable=True)
    time_spent_seconds = Column(Integer, default=0)
    status = Column(String(50), default="completed")
    timestamp = Column(DateTime, default=datetime.utcnow)

    child = relationship("ChildProfile", back_populates="learning_histories")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False)
    content_id = Column(Integer, ForeignKey("learning_contents.id"), nullable=False)
    recommended_by = Column(String(50), default="RuleEngine/Placeholder")
    action_type = Column(String(50), default="same_difficulty")
    confidence_score = Column(Float, default=0.85)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    child = relationship("ChildProfile", back_populates="recommendations")
