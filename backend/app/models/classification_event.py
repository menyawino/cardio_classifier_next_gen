from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from .base import Base

class ClassificationEvent(Base):
    __tablename__ = "classification_events"
    id = Column(Integer, primary_key=True)
    variant_id = Column(Integer, ForeignKey("variants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    classification = Column(String, nullable=False)
    evidence = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
