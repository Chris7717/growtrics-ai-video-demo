from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.db.session import async_session
from app.schemas.video_requests import VideoJobRequest
from app.schemas.video_responses import VideoJobResponse, VideoJobDetailResponse, BaseResponse
from app.repositories.job_repo import job_repo
from app.schemas.dto import VideoJobCreate
from app.queue.asyncio_queue import local_queue

router = APIRouter(prefix="/videos", tags=["Videos"])

async def get_db():
    async with async_session() as session:
        yield session

@router.post("", response_model=VideoJobResponse, status_code=status.HTTP_202_ACCEPTED, summary="Create a new video job")
async def create_video_job(request: VideoJobRequest, db: AsyncSession = Depends(get_db)):
    """
    Creates a new video generation job and adds it to the processing queue.
    """
    job_in = VideoJobCreate(query=request.query)
    job = await job_repo.create(db, obj_in=job_in)
    
    # Publish to queue
    await local_queue.publish("video_jobs", job.id)
    
    return VideoJobResponse(
        message="Video generation request has been queued",
        job_id=job.id
    )

@router.get("", response_model=List[VideoJobDetailResponse], summary="List video jobs")
async def list_video_jobs(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a list of video jobs.
    """
    jobs = await job_repo.get_multi(db, skip=skip, limit=limit)
    return jobs

@router.get("/{job_id}", response_model=VideoJobDetailResponse, summary="Get video job details")
async def get_video_job(job_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieve the status and details of a specific video job.
    """
    job = await job_repo.get(db, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job

@router.get("/{job_id}/artifact", summary="Get final video artifact")
async def get_video_artifact(job_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieve the final video URL or stream.
    """
    job = await job_repo.get(db, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    
    # For now, just return a mock response. In Phase 6 it will return the actual video.
    # Return 409 if not ready
    from app.db.enums import JobStatus
    if job.status != JobStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Video is not ready yet (ARTIFACT_NOT_READY)"
        )
        
    return {"message": "Video is ready", "url": f"http://localhost:8000/artifacts/{job_id}/video/video.mp4"}

@router.get("/{job_id}/events", summary="Get job events")
async def get_video_job_events(job_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieve the event history for a specific video job.
    """
    from app.repositories.event_repo import event_repo
    from sqlalchemy import select
    from app.db.models.job_event import JobEvent
    
    # We could add a custom method in event_repo, but for now we'll query here or just use a generic approach
    result = await db.execute(select(JobEvent).where(JobEvent.job_id == job_id).order_by(JobEvent.created_at))
    events = result.scalars().all()
    return events

