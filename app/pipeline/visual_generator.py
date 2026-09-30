import os
from sqlalchemy.ext.asyncio import AsyncSession
from app.pipeline.context import PipelineContext
from app.renderers.registry import registry
from app.repositories.event_repo import event_repo
from app.schemas.dto import JobEventCreate
from app.db.enums import JobStage, JobStatus

class VisualGenerator:
    async def run(self, session: AsyncSession, context: PipelineContext) -> None:
        """
        Stage 5: Generate Visuals
        - Iterate over scenes and generate visuals.
        """
        plan_data = context.lesson_plan_data
        if not plan_data or "scenes" not in plan_data:
            raise Exception("No scenes found to generate visuals.")

        scenes = plan_data["scenes"]
        job_id_str = str(context.job.id)
        
        # Create artifacts directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        visual_dir = os.path.join(project_root, "artifacts", job_id_str, "visuals")
        os.makedirs(visual_dir, exist_ok=True)
        
        for idx, scene in enumerate(scenes):
            visual_data = scene.get("visual_data", {})
            visual_type = visual_data.get("type", "title_card") # default to title_card
            
            output_path = os.path.join(visual_dir, f"scene_{idx}.mp4")
            
            renderer_class = registry.get(visual_type)
            if not renderer_class:
                print(f"Renderer for {visual_type} not found, falling back to title_card.")
                renderer_class = registry.get("title_card")
                
            renderer = renderer_class()
            
            # Use duration from audio if available, else 5s
            duration = scene.get("audio_duration", 5.0)
            
            # Generate Visual
            success = await renderer.render(visual_data, duration, output_path)
            
            if not success:
                # Static fallback (just a simple image or color block if needed)
                print(f"Visual rendering failed for scene {idx}. Using static fallback.")
                fallback_renderer = registry.get("title_card")()
                success = await fallback_renderer.render({"text": "Fallback"}, duration, output_path)
                if not success:
                    raise Exception("VISUAL_GENERATION_FAILED: Both main renderer and fallback failed.")
                
                context.job.used_fallback = True
                await self._record_event(session, context.job, JobStage.generating_visuals, JobStatus.processing, f"Fallback used for visual scene {idx}")
                
            # Update metadata
            scene["visual_path"] = output_path

    async def _record_event(self, session: AsyncSession, job, stage, status, message: str):
        event_in = JobEventCreate(
            job_id=job.id,
            stage=stage,
            event_type=status.name if hasattr(status, 'name') else str(status),
            message=message
        )
        await event_repo.create(session, obj_in=event_in)
