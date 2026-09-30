import uuid
from sqlalchemy import Column, String, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class LessonPlan(Base):
    __tablename__ = "lesson_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("video_jobs.id"), nullable=False, unique=True)
    source = Column(String, nullable=False) # 'llm' or 'template'
    title = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    learning_objectives = Column(JSON, nullable=True)
    estimated_duration_seconds = Column(Integer, nullable=True)
    
    is_valid = Column(Boolean, default=False, nullable=False)
    validation_errors = Column(JSON, nullable=True)

    job = relationship("VideoJob")
