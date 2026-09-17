from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class ChildProfile(Base):
    __tablename__ = "child_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    date_of_birth = Column(String(50), nullable=True) # DOB string or YYYY-MM-DD
    learning_level = Column(String(50), default="beginner", nullable=False)
    learning_requirements = Column(Text, nullable=True) # Special accommodations notes (non-medical)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="child_profile")
    parent_links = relationship("ParentChild", back_populates="child", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="child", cascade="all, delete-orphan")
    learning_histories = relationship("LearningHistory", back_populates="child", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="child", cascade="all, delete-orphan")
