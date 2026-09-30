from app.repositories.base import BaseRepository
from app.db.models.video_job import VideoJob
from app.schemas.dto import VideoJobCreate, VideoJobUpdate

class VideoJobRepository(BaseRepository[VideoJob, VideoJobCreate, VideoJobUpdate]):
    def __init__(self):
        super().__init__(VideoJob)

job_repo = VideoJobRepository()
