from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import Field
from app.schemas.base import BaseDTO
from app.db.enums import JobStatus, JobStage

class BaseResponse(BaseDTO):
    message: str = Field(
        ...,
        description="A descriptive message indicating the result of the API call.",
        example="Operation successful"
    )

class VideoJobResponse(BaseResponse):
    job_id: UUID = Field(
        ...,
        description="The unique identifier for the created video job.",
        example="123e4567-e89b-12d3-a456-426614174000"
    )

class JobEventResponse(BaseDTO):
    stage: JobStage = Field(..., description="The stage of the pipeline where the event occurred.")
    status: JobStatus = Field(..., description="The status of the job at the time of the event.")
    message: str = Field(..., description="The event log message.")
    created_at: datetime = Field(..., description="When the event occurred.")

class VideoJobDetailResponse(BaseDTO):
    id: UUID = Field(..., description="Job ID")
    query: str = Field(..., description="Original user query")
    status: JobStatus = Field(..., description="Current status of the job")
    current_stage: Optional[JobStage] = Field(None, description="Current stage in the pipeline")
    progress: float = Field(..., description="Progress percentage (0 to 100)")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last updated time")
    events: Optional[List[JobEventResponse]] = Field(None, description="Recent events for the job")
