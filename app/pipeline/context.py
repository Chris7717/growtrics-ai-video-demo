from dataclasses import dataclass, field
from uuid import UUID
from typing import Optional, List, Dict, Any
from app.db.models.video_job import VideoJob
from app.db.models.supported_concept import SupportedConcept

@dataclass
class PipelineContext:
    job_id: UUID
    query: str
    job: Optional[VideoJob] = None
    concept: Optional[SupportedConcept] = None
    lesson_plan_data: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
