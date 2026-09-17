from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class LearningHistory(Base):
    __tablename__ = "learning_histories"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False)
    activity_type = Column(String(50), default="quiz", nullable=False) # quiz, lesson, practice
    activity_id = Column(Integer, nullable=False) # quiz_id or content_id
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    difficulty = Column(String(50), default="easy", nullable=False)
    score = Column(Float, nullable=True) # percentage
    completion_status = Column(String(50), default="completed", nullable=False)
    time_spent = Column(Integer, default=0, nullable=False) # seconds
    is_test_data = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    child = relationship("ChildProfile", back_populates="learning_histories")
    topic = relationship("Topic")
