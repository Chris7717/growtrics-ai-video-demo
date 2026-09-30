import os
from sqlalchemy.ext.asyncio import AsyncSession
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
from app.pipeline.context import PipelineContext
from app.repositories.event_repo import event_repo
from app.repositories.artifact_repo import artifact_repo
from app.schemas.dto import JobEventCreate, ArtifactCreate
from app.db.enums import JobStage, JobStatus, ArtifactType

class VideoComposer:
    async def run(self, session: AsyncSession, context: PipelineContext) -> None:
        """
        Stage 6: Compose Video
        - Generate subtitle file (SRT)
        - Combine visuals and audio using MoviePy
        - Extract thumbnail
        """
        job_id_str = str(context.job.id)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # Directories
        video_dir = os.path.join(project_root, "artifacts", job_id_str, "video")
        subtitle_dir = os.path.join(project_root, "artifacts", job_id_str, "subtitles")
        os.makedirs(video_dir, exist_ok=True)
        os.makedirs(subtitle_dir, exist_ok=True)
        
        final_video_path = os.path.join(video_dir, "video.mp4")
        thumbnail_path = os.path.join(video_dir, "thumbnail.png")
        subtitle_path = os.path.join(subtitle_dir, "captions.srt")
        
        plan_data = context.lesson_plan_data
        scenes = plan_data.get("scenes", [])
        
        # 1. Generate Subtitle (Mock SRT generation updated to use proper durations)
        def format_time(seconds):
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds - int(seconds)) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

        with open(subtitle_path, "w", encoding="utf-8") as f:
            current_time = 0.0
            for i, scene in enumerate(scenes):
                duration = float(scene.get('audio_duration', 5.0))
                start_str = format_time(current_time)
                end_str = format_time(current_time + duration)
                f.write(f"{i+1}\n{start_str} --> {end_str}\n{scene.get('narration', '')}\n\n")
                current_time += duration
        
        await self._save_artifact(session, context.job.id, ArtifactType.subtitle, subtitle_path)
        
        # 2. Compose Video
        clips = []
        try:
            for scene in scenes:
                v_path = scene.get("visual_path")
                a_path = scene.get("audio_path")
                
                if v_path and os.path.exists(v_path):
                    v_clip = VideoFileClip(v_path)
                    if a_path and os.path.exists(a_path):
                        a_clip = AudioFileClip(a_path)
                        v_clip = v_clip.with_audio(a_clip)
                    clips.append(v_clip)
            
            if clips:
                final_clip = concatenate_videoclips(clips, method="compose")
                # Write final video
                final_clip.write_videofile(
                    final_video_path,
                    fps=30,
                    codec="libx264",
                    audio_codec="aac",
                    logger=None
                )
                
                # 3. Generate Thumbnail (First frame of first clip)
                final_clip.save_frame(thumbnail_path, t=0)
                
                for clip in clips:
                    clip.close()
                final_clip.close()
            else:
                print("No clips available to combine, creating mock video file.")
                with open(final_video_path, "w") as f:
                    f.write("mock video data")
                with open(thumbnail_path, "w") as f:
                    f.write("mock thumbnail data")
                    
        except Exception as e:
            print(f"Video composition failed: {e}")
            raise Exception("VIDEO_RENDER_FAILED")
            
        await self._save_artifact(session, context.job.id, ArtifactType.thumbnail, thumbnail_path)
        await self._save_artifact(session, context.job.id, ArtifactType.final_video, final_video_path)

    async def _save_artifact(self, session: AsyncSession, job_id, type_: ArtifactType, path: str):
        artifact_in = ArtifactCreate(
            job_id=job_id,
            artifact_type=type_,
            file_path=path,
            metadata_={}
        )
        await artifact_repo.create(session, obj_in=artifact_in)

    async def _record_event(self, session: AsyncSession, job, stage, status, message: str):
        event_in = JobEventCreate(
            job_id=job.id,
            stage=stage,
            event_type=status.name if hasattr(status, 'name') else str(status),
            message=message
        )
        await event_repo.create(session, obj_in=event_in)
