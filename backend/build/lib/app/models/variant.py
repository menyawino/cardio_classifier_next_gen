from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from .base import Base

class Variant(Base):
    __tablename__ = "variants"
    id = Column(Integer, primary_key=True)
    hgvs = Column(String, index=True, nullable=False)
    genome_build = Column(String, default="GRCh38")
    classification = Column(String, nullable=False)
    evidence = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
