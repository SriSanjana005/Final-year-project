from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
from app.models.user import User, UserRole

class ChildProfile(Base):
    __tablename__ = "child_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    age = Column(Integer, nullable=True)
    learning_level = Column(String(50), default="beginner")
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="child_profile")
    parent_links = relationship("ParentChild", back_populates="child")
    quiz_attempts = relationship("QuizAttempt", back_populates="child")
    learning_histories = relationship("LearningHistory", back_populates="child")
    recommendations = relationship("Recommendation", back_populates="child")

class ParentProfile(Base):
    __tablename__ = "parent_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    phone_number = Column(String(50), nullable=True)

    user = relationship("User", back_populates="parent_profile")
    children_links = relationship("ParentChild", back_populates="parent")

class ParentChild(Base):
    __tablename__ = "parent_child_mappings"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parent_profiles.id"), nullable=False)
    child_id = Column(Integer, ForeignKey("child_profiles.id"), nullable=False)
    relationship_type = Column(String(50), default="parent")

    parent = relationship("ParentProfile", back_populates="children_links")
    child = relationship("ChildProfile", back_populates="parent_links")

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    icon_name = Column(String(50), default="book")
    created_at = Column(DateTime, default=datetime.utcnow)

    contents = relationship("LearningContent", back_populates="topic")
    quizzes = relationship("Quiz", back_populates="topic")

class LearningContent(Base):
    __tablename__ = "learning_contents"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content_body = Column(Text, nullable=False)
    media_url = Column(String(500), nullable=True)
    difficulty_level = Column(Integer, default=1)
    estimated_minutes = Column(Integer, default=5)
    is_approved = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    topic = relationship("Topic", back_populates="contents")

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    passing_percentage = Column(Integer, default=70)
    created_at = Column(DateTime, default=datetime.utcnow)

    topic = relationship("Topic", back_populates="quizzes")
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
    child_id = Column(Integer, ForeignKey("child_profiles.id"), nullable=False)
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
    child_id = Column(Integer, ForeignKey("child_profiles.id"), nullable=False)
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
    child_id = Column(Integer, ForeignKey("child_profiles.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("learning_contents.id"), nullable=False)
    recommended_by = Column(String(50), default="RuleEngine/Placeholder")
    action_type = Column(String(50), default="same_difficulty")
    confidence_score = Column(Float, default=0.85)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    child = relationship("ChildProfile", back_populates="recommendations")
