from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.base import BaseDTO
from app.db.enums import JobStatus, JobStage, ArtifactType, ArtifactStatus

class SupportedConceptCreate(BaseModel):
    code: str
    canonical_query: str
    title: str
    required_facts: List[str]
    allowed_visual_types: List[str]
    template_path: str
    is_active: bool = True

class SupportedConceptUpdate(BaseModel):
    canonical_query: Optional[str] = None
    title: Optional[str] = None
    required_facts: Optional[List[str]] = None
    allowed_visual_types: Optional[List[str]] = None
    template_path: Optional[str] = None
    is_active: Optional[bool] = None

class VideoJobCreate(BaseModel):
    concept_id: Optional[UUID] = None
    query: str
    status: JobStatus = JobStatus.queued
    current_stage: JobStage = JobStage.resolving_concept
    error_message: Optional[str] = None
    progress: float = 0.0

class VideoJobUpdate(BaseModel):
    concept_id: Optional[UUID] = None
    status: Optional[JobStatus] = None
    current_stage: Optional[JobStage] = None
    error_message: Optional[str] = None
    progress: Optional[float] = None

class LessonPlanCreate(BaseModel):
    job_id: UUID
    source: str
    title: str
    summary: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    estimated_duration_seconds: Optional[int] = None
    is_valid: bool = False
    validation_errors: Optional[List[str]] = None

class LessonPlanUpdate(BaseModel):
    source: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    estimated_duration_seconds: Optional[int] = None
    is_valid: Optional[bool] = None
    validation_errors: Optional[List[str]] = None

class LessonSceneCreate(BaseModel):
    pass

class LessonSceneUpdate(BaseModel):
    pass


class ArtifactCreate(BaseModel):
    job_id: UUID
    artifact_type: ArtifactType
    status: ArtifactStatus = ArtifactStatus.pending
    file_path: str
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None
    metadata_: Optional[Dict[str, Any]] = Field(default=None, alias="metadata")

class ArtifactUpdate(BaseModel):
    status: Optional[ArtifactStatus] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None
    metadata_: Optional[Dict[str, Any]] = Field(default=None, alias="metadata")

class JobEventCreate(BaseModel):
    job_id: UUID
    stage: Optional[JobStage] = None
    event_type: str
    message: str
    event_metadata: Optional[Dict[str, Any]] = None

class JobEventUpdate(BaseModel):
    message: Optional[str] = None
    event_metadata: Optional[Dict[str, Any]] = None
