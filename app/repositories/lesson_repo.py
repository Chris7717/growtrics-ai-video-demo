from app.repositories.base import BaseRepository
from app.db.models.lesson_plan import LessonPlan
from app.db.models.lesson_scene import LessonScene
from app.schemas.dto import LessonPlanCreate, LessonPlanUpdate, LessonSceneCreate, LessonSceneUpdate

class LessonPlanRepository(BaseRepository[LessonPlan, LessonPlanCreate, LessonPlanUpdate]):
    def __init__(self):
        super().__init__(LessonPlan)

class LessonSceneRepository(BaseRepository[LessonScene, LessonSceneCreate, LessonSceneUpdate]):
    def __init__(self):
        super().__init__(LessonScene)

lesson_plan_repo = LessonPlanRepository()
lesson_scene_repo = LessonSceneRepository()
