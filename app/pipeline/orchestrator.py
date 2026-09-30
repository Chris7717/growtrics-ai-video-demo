from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.video_job import VideoJob
from app.pipeline.context import PipelineContext
from app.pipeline.concept_resolver import ConceptResolver
from app.pipeline.lesson_planner import LessonPlanner
from app.pipeline.lesson_validator import LessonValidator
from app.repositories.job_repo import job_repo
from app.repositories.event_repo import event_repo
from app.schemas.dto import VideoJobUpdate, JobEventCreate
from app.db.enums import JobStage, JobStatus

class VideoPipeline:
    def __init__(self):
        self.resolver = ConceptResolver()
        self.planner = LessonPlanner()
        self.validator = LessonValidator()

    async def run_pipeline(self, session: AsyncSession, job: VideoJob):
        context = PipelineContext(job_id=job.id, query=job.query, job=job)
        
        try:
            # Stage 1: Resolve Concept
            await self._update_stage(session, job, JobStage.resolving_concept, 5)
            await self.resolver.run(session, context)
            
            # Stage 2: Plan Lesson
            await self._update_stage(session, job, JobStage.planning_lesson, 15)
            await self.planner.run(session, context)
            
            # Stage 3: Validate and DB write
            await self._update_stage(session, job, JobStage.validating_lesson, 25)
            await self.validator.run(session, context)
            
            # Stage 4: Generate Audio
            await self._update_stage(session, job, JobStage.generating_audio, 40)
            from app.pipeline.audio_generator import AudioGenerator
            audio_generator = AudioGenerator()
            await audio_generator.run(session, context)
            
            # Stage 5: Generate Visuals
            await self._update_stage(session, job, JobStage.generating_visuals, 60)
            from app.pipeline.visual_generator import VisualGenerator
            visual_generator = VisualGenerator()
            await visual_generator.run(session, context)
            
            # Stage 6: Video Composition
            await self._update_stage(session, job, JobStage.rendering_video, 80)
            from app.pipeline.video_composer import VideoComposer
            video_composer = VideoComposer()
            await video_composer.run(session, context)
            
            # Stage 7: Validate Video
            await self._update_stage(session, job, JobStage.validating_video, 95)
            from app.pipeline.video_validator import VideoValidator
            video_validator = VideoValidator()
            await video_validator.run(session, context)
            
            # Phase 7 Completion
            await self._record_event(session, job, JobStage.validating_video, JobStatus.completed, "Pipeline Phase 7 Completed - All Done")

        except Exception as e:
            # Handle Failure
            await self._record_event(session, job, job.current_stage, JobStatus.failed, str(e))
            raise e

    async def _update_stage(self, session: AsyncSession, job: VideoJob, stage: JobStage, progress: int):
        await job_repo.update(session, db_obj=job, obj_in=VideoJobUpdate(current_stage=stage, progress=progress))
        
    async def _record_event(self, session: AsyncSession, job, stage, status, message: str):
        event_in = JobEventCreate(
            job_id=job.id,
            stage=stage,
            event_type=status.name if hasattr(status, 'name') else str(status),
            message=message
        )
        await event_repo.create(session, obj_in=event_in)
