import os
import subprocess
from sqlalchemy.ext.asyncio import AsyncSession
from app.pipeline.context import PipelineContext
from app.providers.tts.edge_tts_provider import EdgeTTSProvider
from app.repositories.job_repo import job_repo
from app.repositories.event_repo import event_repo
from app.schemas.dto import VideoJobUpdate, JobEventCreate
from app.db.enums import JobStage, JobStatus

class AudioGenerator:
    def __init__(self):
        self.tts_provider = EdgeTTSProvider()
        
    async def run(self, session: AsyncSession, context: PipelineContext) -> None:
        """
        Stage 4: Generate Audio
        - Iterate over scenes and generate TTS.
        - Determine duration using ffprobe (or mock if not installed).
        """
        plan_data = context.lesson_plan_data
        if not plan_data or "scenes" not in plan_data:
            raise Exception("No scenes found to generate audio.")

        scenes = plan_data["scenes"]
        job_id_str = str(context.job.id)
        
        # Create artifacts directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        audio_dir = os.path.join(project_root, "artifacts", job_id_str, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        
        for idx, scene in enumerate(scenes):
            narration = scene.get("narration")
            if not narration:
                continue
                
            output_path = os.path.join(audio_dir, f"scene_{idx}.mp3")
            
            # Retry logic
            success = False
            for attempt in range(2):
                success = await self.tts_provider.generate_audio(narration, output_path)
                if success:
                    break
                else:
                    await self._record_event(session, context.job, JobStage.generating_audio, JobStatus.processing, f"TTS generation failed for scene {idx}, retry {attempt + 1}")
            
            if not success:
                raise Exception("AUDIO_GENERATION_FAILED: Max retries reached for TTS.")
                
            # Get duration (mocking ffprobe for simplicity unless ffmpeg is required)
            # In a real scenario we'd use subprocess.run(['ffprobe', ...])
            duration = 5.0 # default mock duration
            try:
                result = subprocess.run(
                    ['ffprobe', '-i', output_path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0'],
                    capture_output=True, text=True
                )
                if result.stdout:
                    duration = float(result.stdout.strip())
            except FileNotFoundError:
                print("ffprobe not found, using mock duration.")
            except Exception as e:
                print(f"Failed to get duration with ffprobe: {e}")
                
            # Update scene metadata in context (we will save this later or immediately in a real app)
            scene["audio_path"] = output_path
            scene["audio_duration"] = duration

    async def _record_event(self, session: AsyncSession, job, stage, status, message: str):
        event_in = JobEventCreate(
            job_id=job.id,
            stage=stage,
            event_type=status.name if hasattr(status, 'name') else str(status),
            message=message
        )
        await event_repo.create(session, obj_in=event_in)
