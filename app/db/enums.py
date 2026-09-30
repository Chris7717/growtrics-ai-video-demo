import enum

class JobStatus(str, enum.Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class JobStage(str, enum.Enum):
    resolving_concept = "resolving_concept"
    planning_lesson = "planning_lesson"
    validating_lesson = "validating_lesson"
    generating_audio = "generating_audio"
    generating_visuals = "generating_visuals"
    rendering_video = "rendering_video"
    validating_video = "validating_video"

class ArtifactType(str, enum.Enum):
    lesson_plan = "lesson_plan"
    scene_audio = "scene_audio"
    scene_visual = "scene_visual"
    subtitle = "subtitle"
    thumbnail = "thumbnail"
    final_video = "final_video"

class ArtifactStatus(str, enum.Enum):
    pending = "pending"
    ready = "ready"
    invalid = "invalid"
