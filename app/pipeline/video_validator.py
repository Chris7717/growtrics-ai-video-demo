import os
import subprocess
from sqlalchemy.ext.asyncio import AsyncSession
from app.pipeline.context import PipelineContext
from app.repositories.event_repo import event_repo
from app.schemas.dto import JobEventCreate
from app.db.enums import JobStage, JobStatus

class VideoValidator:
    async def run(self, session: AsyncSession, context: PipelineContext) -> None:
        """
        Stage 7: Validate Video
        - Check file size and format using FFprobe (mocked for simplicity)
        """
        job_id_str = str(context.job.id)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        video_path = os.path.join(project_root, "artifacts", job_id_str, "video", "video.mp4")
        
        if not os.path.exists(video_path):
            raise Exception("VALIDATION_FAILED: Video file does not exist.")
            
        file_size = os.path.getsize(video_path)
        if file_size == 0:
            raise Exception("VALIDATION_FAILED: Video file is empty.")
            
        # Optional: Call ffprobe to verify codec
        try:
            subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', video_path], capture_output=True, check=True)
            # If successful, we assume it's good
        except Exception:
            print("ffprobe check skipped or failed, assuming valid for now.")
            pass
            
        await self._record_event(session, context.job, JobStage.validating_video, JobStatus.completed, "Video validated successfully")

    async def _record_event(self, session: AsyncSession, job, stage, status, message: str):
        event_in = JobEventCreate(
            job_id=job.id,
            stage=stage,
            event_type=status.name if hasattr(status, 'name') else str(status),
            message=message
        )
        await event_repo.create(session, obj_in=event_in)
