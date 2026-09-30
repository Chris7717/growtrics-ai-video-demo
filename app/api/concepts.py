from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import async_session
from app.repositories.concept_repo import concept_repo
from app.schemas.dto import SupportedConceptCreate, SupportedConceptUpdate
from app.db.models.supported_concept import SupportedConcept
from pydantic import BaseModel
from uuid import UUID

class ConceptResponse(BaseModel):
    id: UUID
    code: str
    canonical_query: str
    title: str
    required_facts: List[str]
    allowed_visual_types: List[str]
    template_path: str
    is_active: bool

    class Config:
        from_attributes = True

router = APIRouter(prefix="/concepts", tags=["Concepts"])

async def get_db():
    async with async_session() as session:
        yield session

@router.get("", response_model=List[ConceptResponse], summary="List supported concepts")
async def list_concepts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Retrieve all supported concepts that can be used for video generation.
    """
    concepts = await concept_repo.get_multi(db, skip=skip, limit=limit)
    return concepts
