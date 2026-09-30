from app.repositories.base import BaseRepository
from app.db.models.job_event import JobEvent
from app.schemas.dto import JobEventCreate, JobEventUpdate

class JobEventRepository(BaseRepository[JobEvent, JobEventCreate, JobEventUpdate]):
    def __init__(self):
        super().__init__(JobEvent)

event_repo = JobEventRepository()
