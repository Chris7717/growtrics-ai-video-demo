import asyncio
from uuid import UUID
from app.queue.interface import BaseQueue
from app.db.session import async_session
from app.repositories.job_repo import job_repo
from app.schemas.dto import VideoJobUpdate
from app.db.enums import JobStatus, JobStage

class VideoWorker:
    def __init__(self, queue: BaseQueue, queue_name: str = "video_jobs"):
        self.queue = queue
        self.queue_name = queue_name

    async def start(self):
        print("Worker starting...")
        asyncio.create_task(self.queue.consume(self.queue_name, self.process_job))

    async def process_job(self, job_id: UUID):
        print(f"Worker received job: {job_id}")
        async with async_session() as session:
            job = await job_repo.get(session, job_id)
            if not job:
                print(f"Job {job_id} not found")
                return

            try:
                # Mark as processing
                await job_repo.update(session, db_obj=job, obj_in=VideoJobUpdate(status=JobStatus.processing))
                
                # Run actual pipeline
                from app.pipeline.orchestrator import VideoPipeline
                pipeline = VideoPipeline()
                print(f"Processing job {job_id}...")
                await pipeline.run_pipeline(session, job)
                
                # Mark as completed
                await job_repo.update(
                    session, 
                    db_obj=job, 
                    obj_in=VideoJobUpdate(status=JobStatus.completed, progress=100.0)
                )
                print(f"Job {job_id} completed successfully.")

            except Exception as e:
                print(f"Job {job_id} failed: {e}")
                # Re-fetch in case of session invalidation
                job = await job_repo.get(session, job_id)
                if job:
                    await job_repo.update(
                        session, 
                        db_obj=job, 
                        obj_in=VideoJobUpdate(status=JobStatus.failed, error_message=str(e))
                    )
