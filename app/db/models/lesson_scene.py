import uuid
from sqlalchemy import Column, String, Integer, JSON, ForeignKey
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class LessonScene(Base):
    __tablename__ = "lesson_scenes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("video_jobs.id"), nullable=False)
    scene_index = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    narration = Column(String, nullable=False)
    on_screen_text = Column(JSON, nullable=True)
    visual_type = Column(String, nullable=False)
    visual_data = Column(JSON, nullable=True)
    planned_duration_seconds = Column(Integer, nullable=True)
    actual_duration_seconds = Column(Integer, nullable=True)

    job = relationship("VideoJob")
