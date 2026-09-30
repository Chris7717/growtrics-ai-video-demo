import uuid
from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, Enum
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.db.enums import ArtifactType, ArtifactStatus

class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("video_jobs.id"), nullable=False)
    artifact_type = Column(Enum(ArtifactType), nullable=False)
    status = Column(Enum(ArtifactStatus), default=ArtifactStatus.pending, nullable=False)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)

    job = relationship("VideoJob")
