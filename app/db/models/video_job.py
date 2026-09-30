import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, Float, DateTime, ForeignKey, Enum
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.db.enums import JobStatus, JobStage

class VideoJob(Base):
    __tablename__ = "video_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query = Column(String, nullable=False)
    normalized_query = Column(String, nullable=True)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("supported_concepts.id"), nullable=True)
    
    status = Column(Enum(JobStatus), default=JobStatus.queued, nullable=False)
    current_stage = Column(Enum(JobStage), nullable=True)
    progress = Column(Integer, default=0, nullable=False)
    
    retry_count = Column(Integer, default=0, nullable=False)
    used_fallback = Column(Boolean, default=False, nullable=False)
    
    error_code = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    estimated_cost_usd = Column(Float, nullable=True)
    
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    concept = relationship("SupportedConcept")
