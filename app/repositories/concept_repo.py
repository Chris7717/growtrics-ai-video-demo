from app.repositories.base import BaseRepository
from app.db.models.supported_concept import SupportedConcept
from app.schemas.dto import SupportedConceptCreate, SupportedConceptUpdate

class SupportedConceptRepository(BaseRepository[SupportedConcept, SupportedConceptCreate, SupportedConceptUpdate]):
    def __init__(self):
        super().__init__(SupportedConcept)

concept_repo = SupportedConceptRepository()
