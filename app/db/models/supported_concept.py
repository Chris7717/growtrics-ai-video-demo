import uuid
from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.types import Uuid as UUID
from app.db.base import Base

class SupportedConcept(Base):
    __tablename__ = "supported_concepts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, index=True, nullable=False)
    canonical_query = Column(String, nullable=False)
    title = Column(String, nullable=False)
    required_facts = Column(JSON, nullable=False)
    allowed_visual_types = Column(JSON, nullable=False)
    template_path = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
