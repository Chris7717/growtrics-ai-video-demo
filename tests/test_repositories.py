import pytest
from uuid import UUID
from app.repositories.concept_repo import concept_repo
from app.repositories.job_repo import job_repo
from app.schemas.dto import SupportedConceptCreate, SupportedConceptUpdate, VideoJobCreate
from app.db.enums import JobStatus, JobStage

@pytest.mark.asyncio
async def test_create_and_get_concept(db_session):
    # 1. Create
    concept_in = SupportedConceptCreate(
        code="test_concept",
        canonical_query="Test query",
        title="Test Title",
        required_facts=["Fact 1", "Fact 2"],
        allowed_visual_types=["diagram"],
        template_path="templates/test.json",
        is_active=True
    )
    concept = await concept_repo.create(db_session, obj_in=concept_in)
    
    assert concept.id is not None
    assert concept.code == "test_concept"
    
    # 2. Get
    fetched_concept = await concept_repo.get(db_session, concept.id)
    assert fetched_concept is not None
    assert fetched_concept.title == "Test Title"

@pytest.mark.asyncio
async def test_update_concept(db_session):
    # Create first
    concept_in = SupportedConceptCreate(
        code="test_update_concept",
        canonical_query="Query",
        title="Title",
        required_facts=[],
        allowed_visual_types=[],
        template_path="path",
        is_active=True
    )
    concept = await concept_repo.create(db_session, obj_in=concept_in)
    
    # Update
    update_in = SupportedConceptUpdate(title="Updated Title")
    updated_concept = await concept_repo.update(db_session, db_obj=concept, obj_in=update_in)
    
    assert updated_concept.title == "Updated Title"
    
    # Verify DB
    fetched = await concept_repo.get(db_session, concept.id)
    assert fetched.title == "Updated Title"

@pytest.mark.asyncio
async def test_create_video_job(db_session):
    # Create Concept
    concept_in = SupportedConceptCreate(
        code="concept_for_job",
        canonical_query="Q",
        title="T",
        required_facts=[],
        allowed_visual_types=[],
        template_path="",
        is_active=True
    )
    concept = await concept_repo.create(db_session, obj_in=concept_in)
    
    # Create Job
    job_in = VideoJobCreate(
        concept_id=concept.id,
        query="How does it work?"
    )
    job = await job_repo.create(db_session, obj_in=job_in)
    
    assert job.id is not None
    assert job.concept_id == concept.id
    assert job.status == JobStatus.queued
    assert job.current_stage == JobStage.resolving_concept
