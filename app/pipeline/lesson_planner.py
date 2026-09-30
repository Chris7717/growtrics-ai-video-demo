import json
import os
from sqlalchemy.ext.asyncio import AsyncSession
from app.pipeline.context import PipelineContext
from app.config import settings

class LessonPlanner:
    async def run(self, session: AsyncSession, context: PipelineContext) -> None:
        """
        Stage 2: Plan Lesson
        - Calls Gemini LLM to generate lesson plan (mocked here or use template)
        - Uses template fallback if no API key
        """
        api_key = settings.GEMINI_API_KEY
        if api_key:
            try:
                print("Generating lesson plan using Gemini LLM...")
                from google import genai
                from google.genai import types
                
                client = genai.Client(api_key=api_key)
                
                schema = {
                    "type": "OBJECT",
                    "properties": {
                        "title": {"type": "STRING"},
                        "target_audience": {"type": "STRING"},
                        "learning_objectives": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"}
                        },
                        "scenes": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "narration": {"type": "STRING", "description": "The script to be spoken (must answer user queries)"},
                                    "on_screen_text": {
                                        "type": "ARRAY",
                                        "items": {"type": "STRING"}
                                    },
                                    "visual_data": {
                                        "type": "OBJECT",
                                        "properties": {
                                            "type": {"type": "STRING"},
                                            "text": {"type": "STRING"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "required": ["title", "target_audience", "learning_objectives", "scenes"]
                }
                
                prompt = f"""
                You are an educational video script writer.
                Generate a comprehensive video script in JSON format that answers the following query:
                '{context.job.query}'
                
                The script must contain multiple scenes to fully explain the topic.
                Each scene must have narration, on-screen text, and visual data (e.g., {{"type": "title_card", "text": "Topic Title"}}).
                """
                
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema,
                        temperature=0.7,
                    ),
                )
                
                print(f"Gemini API Response:\n{response.text}\n")
                
                from app.repositories.event_repo import event_repo
                from app.schemas.dto import JobEventCreate
                from app.db.enums import JobStage, JobStatus
                
                # Log to DB so it shows on UI
                event_in = JobEventCreate(
                    job_id=context.job.id,
                    stage=JobStage.planning_lesson,
                    event_type=JobStatus.processing,
                    message=f"Gemini Generated Script: {response.text}" 
                )
                await event_repo.create(session, obj_in=event_in)

                context.lesson_plan_data = json.loads(response.text)
                context.job.used_fallback = False
                return
            except Exception as e:
                print(f"Gemini API failed: {e}. Falling back to template.")
                
        # Fallback to template
        print("Using template fallback for lesson plan...")
        template_path = context.concept.template_path
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        full_path = os.path.join(project_root, template_path)
        
        try:
            if not os.path.exists(full_path):
                context.lesson_plan_data = self._create_mock_lesson_plan(context.job.query)
            else:
                with open(full_path, "r", encoding="utf-8") as f:
                    context.lesson_plan_data = json.load(f)
                    
            context.job.used_fallback = True
        except Exception as e:
            raise Exception(f"Failed to generate lesson plan: {str(e)}")

    def _create_mock_lesson_plan(self, title: str) -> dict:
        return {
            "title": f"Lesson about {title}",
            "target_audience": "Beginner",
            "learning_objectives": ["Understand the basic concept", "Learn how it applies"],
            "scenes": [
                {
                    "narration": "Welcome to the lesson.",
                    "on_screen_text": ["Welcome"],
                    "visual_data": {"type": "title_card", "text": "Welcome"}
                },
                {
                    "narration": "Let's dive into the details.",
                    "on_screen_text": ["Details"],
                    "visual_data": {"type": "title_card", "text": "Details"}
                }
            ]
        }
