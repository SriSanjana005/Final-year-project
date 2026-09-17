from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class LearningContent(Base):
    __tablename__ = "learning_contents"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(String(50), default="lesson", nullable=False) # lesson, video, practice, activity
    content_body = Column(Text, nullable=False)
    difficulty = Column(String(50), default="easy", nullable=False) # easy, medium, hard
    estimated_duration = Column(Integer, default=10, nullable=False) # duration in minutes
    is_published = Column(Boolean, default=False, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    topic = relationship("Topic", back_populates="contents")
    creator = relationship("User")
