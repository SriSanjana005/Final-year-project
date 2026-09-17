from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False)
    content_id = Column(Integer, ForeignKey("learning_contents.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    target_difficulty = Column(String(50), default="easy", nullable=False)
    reason = Column(Text, nullable=False)
    recommendation_type = Column(String(50), default="rule_based", nullable=False)
    status = Column(String(50), default="recommended", nullable=False) # recommended, viewed, completed, dismissed
    avg_score = Column(Float, nullable=True)
    is_test_data = Column(Boolean, default=False, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    child = relationship("ChildProfile", back_populates="recommendations")
    content = relationship("LearningContent")
    topic = relationship("Topic")
