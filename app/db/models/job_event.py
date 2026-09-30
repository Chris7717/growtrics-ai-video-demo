import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, JSON, ForeignKey, DateTime, Enum
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.db.enums import JobStage

class JobEvent(Base):
    __tablename__ = "job_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("video_jobs.id"), nullable=False)
    event_type = Column(String, nullable=False)
    stage = Column(Enum(JobStage), nullable=True)
    message = Column(String, nullable=True)
    event_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    job = relationship("VideoJob")
