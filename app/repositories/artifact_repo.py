from app.repositories.base import BaseRepository
from app.db.models.artifact import Artifact
from app.schemas.dto import ArtifactCreate, ArtifactUpdate

class ArtifactRepository(BaseRepository[Artifact, ArtifactCreate, ArtifactUpdate]):
    def __init__(self):
        super().__init__(Artifact)

artifact_repo = ArtifactRepository()
