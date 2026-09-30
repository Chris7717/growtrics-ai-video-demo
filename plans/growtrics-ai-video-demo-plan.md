# Growtrics AI Video Demo — Implementation Plan

## 1. Mục tiêu

Xây dựng backend demo tạo video giải thích hóa học bằng AI với FastAPI, worker bất đồng bộ và PostgreSQL.

Phạm vi demo tập trung vào ba learner query bắt buộc:

1. How does the pH scale work?
2. Why do atoms form covalent bonds?
3. What is the difference between ionic and covalent bonding?

Hệ thống cần:

- Nhận learner query qua API.
- Tạo video job ở trạng thái `queued`.
- Cho worker xử lý bất đồng bộ.
- Theo dõi trạng thái và tiến độ của job.
- Tạo lesson plan và scene.
- Sinh audio, visual, subtitle và final video.
- Lưu metadata artifact trong database.
- Lưu file artifact trên local filesystem.
- Cho phép client lấy hoặc mở final video.
- Có retry, fallback và failure state rõ ràng.

---

## 2. Phạm vi của schema demo

Schema demo chỉ giữ lại sáu bảng:

```text
supported_concepts
video_jobs
lesson_plans
lesson_scenes
artifacts
job_events
```

Quan hệ chính:

```text
supported_concepts
        ↓
video_jobs
        ↓
lesson_plans
        ↓
lesson_scenes
        ↓
artifacts

video_jobs
        ↓
job_events
```

Các thành phần production như provider billing, distributed locking, worker heartbeat, generation attempts riêng biệt và artifact validation table được loại bỏ.

Thông tin retry, fallback và provider được lưu trong `job_events.metadata`.

Thông tin validation của media được lưu trong `artifacts.metadata`.

---

## 3. Kiến trúc tổng thể

```text
Client
  │
  │ POST /api/v1/videos
  ▼
FastAPI
  │
  ├── VideoJobService
  ├── JobRepository
  └── JobQueue
        │
        ▼
     Video Worker
        │
        ├── Concept Resolver
        ├── Lesson Planner
        ├── Lesson Validator
        ├── Scene Builder
        ├── Audio Generator
        ├── Visual Renderer
        ├── Video Composer
        └── Video Validator
        │
        ▼
PostgreSQL + Local Artifact Storage
```

### FastAPI

Chịu trách nhiệm:

- Validate request.
- Tạo `video_jobs`.
- Đưa `job_id` vào queue.
- Trả HTTP `202 Accepted`.
- Liệt kê job.
- Lấy chi tiết job.
- Trả final video artifact.

### Worker

Chịu trách nhiệm:

- Lấy job từ queue.
- Cập nhật `status`, `current_stage` và `progress`.
- Tạo lesson plan và scene.
- Sinh media artifact.
- Retry và fallback khi cần.
- Ghi event vào `job_events`.
- Đánh dấu job `completed` hoặc `failed`.

### PostgreSQL

Lưu:

- Concept được hỗ trợ.
- Job state.
- Lesson plan.
- Scene.
- Metadata artifact.
- Lịch sử job event.

### Local Artifact Storage

Lưu:

- Lesson plan JSON.
- Audio từng scene.
- Visual từng scene.
- Subtitle.
- Thumbnail.
- Final video MP4.

---

## 4. Cấu trúc thư mục

```text
app/
├── main.py
├── config.py
├── dependencies.py
│
├── api/
│   ├── router.py
│   └── videos.py
│
├── db/
│   ├── base.py
│   ├── session.py
│   └── models/
│       ├── supported_concept.py
│       ├── video_job.py
│       ├── lesson_plan.py
│       ├── lesson_scene.py
│       ├── artifact.py
│       └── job_event.py
│
├── schemas/
│   ├── video_requests.py
│   ├── video_responses.py
│   ├── lesson.py
│   └── artifact.py
│
├── repositories/
│   ├── supported_concept_repository.py
│   ├── video_job_repository.py
│   ├── lesson_repository.py
│   ├── artifact_repository.py
│   └── job_event_repository.py
│
├── services/
│   ├── video_job_service.py
│   ├── artifact_service.py
│   └── event_service.py
│
├── queue/
│   ├── interface.py
│   └── asyncio_queue.py
│
├── workers/
│   ├── video_worker.py
│   └── pipeline_context.py
│
├── pipeline/
│   ├── orchestrator.py
│   ├── concept_resolver.py
│   ├── lesson_planner.py
│   ├── lesson_validator.py
│   ├── scene_builder.py
│   ├── audio_generator.py
│   ├── visual_generator.py
│   ├── video_composer.py
│   └── video_validator.py
│
├── providers/
│   ├── llm/
│   │   ├── interface.py
│   │   ├── template_provider.py
│   │   └── gemini_provider.py
│   ├── tts/
│   │   ├── interface.py
│   │   └── edge_tts_provider.py
│   └── storage/
│       ├── interface.py
│       └── local_storage.py
│
├── renderers/
│   ├── registry.py
│   ├── title_card.py
│   ├── ph_scale.py
│   ├── electron_sharing.py
│   ├── electron_transfer.py
│   ├── comparison_table.py
│   └── summary_card.py
│
├── templates/
│   ├── ph_scale.json
│   ├── covalent_bonds.json
│   └── ionic_vs_covalent.json
│
└── artifacts/
```

---

## 5. Database Models

## 5.1. supported_concepts

Mục đích:

- Khai báo các concept mà demo hỗ trợ.
- Chứa rule validation cơ bản.
- Chứa danh sách visual type hợp lệ.
- Chỉ ra curated template dùng làm fallback.

Dữ liệu mẫu:

```json
{
  "code": "ph_scale",
  "canonical_query": "How does the pH scale work?",
  "title": "How the pH Scale Works",
  "required_facts": [
    "The pH scale commonly runs from 0 to 14",
    "pH 7 is neutral",
    "Values below 7 are acidic",
    "Values above 7 are basic",
    "Each whole step represents a tenfold change"
  ],
  "allowed_visual_types": [
    "title_card",
    "ph_scale",
    "comparison_table",
    "summary_card"
  ],
  "template_path": "app/templates/ph_scale.json",
  "is_active": true
}
```

Seed ba concept ngay khi khởi tạo database.

---

## 5.2. video_jobs

Đây là nguồn trạng thái chính của hệ thống.

Các field quan trọng:

- `query`: câu hỏi nguyên bản.
- `normalized_query`: query sau khi chuẩn hóa.
- `concept_id`: concept được nhận diện.
- `status`: trạng thái tổng thể.
- `current_stage`: pipeline stage hiện tại.
- `progress`: tiến độ từ 0 đến 100.
- `retry_count`: số lần retry.
- `used_fallback`: đã sử dụng fallback hay chưa.
- `error_code`: mã lỗi cuối cùng.
- `error_message`: mô tả lỗi.
- `estimated_cost_usd`: chi phí ước tính.
- `started_at`: worker bắt đầu xử lý.
- `completed_at`: job hoàn thành.

State tổng thể:

```text
queued
processing
completed
failed
```

Stage chi tiết:

```text
resolving_concept
planning_lesson
validating_lesson
generating_audio
generating_visuals
rendering_video
validating_video
```

---

## 5.3. lesson_plans

Mỗi job chỉ giữ một lesson plan cuối cùng.

Nếu LLM output không hợp lệ:

1. Retry LLM.
2. Nếu vẫn lỗi, load curated template.
3. Ghi đè lesson plan bằng fallback.
4. Đặt `source = fallback_template`.
5. Đặt `video_jobs.used_fallback = true`.

Các field chính:

- `source`
- `title`
- `summary`
- `learning_objectives`
- `estimated_duration_seconds`
- `is_valid`
- `validation_errors`

---

## 5.4. lesson_scenes

Mỗi scene mô tả một đoạn trong video.

Ví dụ:

```json
{
  "scene_index": 2,
  "title": "Reading the pH Scale",
  "narration": "Seven is neutral. Values below seven are acidic, while values above seven are basic.",
  "on_screen_text": [
    "0–6: Acidic",
    "7: Neutral",
    "8–14: Basic"
  ],
  "visual_type": "ph_scale",
  "visual_data": {
    "minimum": 0,
    "maximum": 14,
    "neutral": 7
  },
  "planned_duration_seconds": 10
}
```

Worker cập nhật `actual_duration_seconds` sau khi audio được tạo.

---

## 5.5. artifacts

Lưu metadata của file trên local filesystem.

Các artifact có thể gồm:

```text
lesson_plan
scene_audio
scene_visual
subtitle
thumbnail
final_video
```

Ví dụ final video:

```json
{
  "artifact_type": "final_video",
  "status": "ready",
  "file_path": "artifacts/{job_id}/video.mp4",
  "file_name": "video.mp4",
  "mime_type": "video/mp4",
  "file_size_bytes": 10485760,
  "duration_seconds": 62.4,
  "metadata": {
    "ffprobe_readable": true,
    "has_video_stream": true,
    "has_audio_stream": true,
    "resolution": "1280x720",
    "video_codec": "h264",
    "audio_codec": "aac"
  }
}
```

---

## 5.6. job_events

Thay thế cho generation attempts và provider calls trong demo.

Ví dụ event retry:

```json
{
  "event_type": "retry",
  "stage": "generating_audio",
  "message": "TTS request timed out. Retrying scene 2.",
  "metadata": {
    "attempt": 2,
    "scene_index": 2,
    "provider": "edge_tts",
    "error_code": "TTS_TIMEOUT"
  }
}
```

Ví dụ fallback:

```json
{
  "event_type": "fallback_used",
  "stage": "planning_lesson",
  "message": "LLM lesson plan failed validation. Using curated template.",
  "metadata": {
    "provider": "gemini",
    "fallback": "ph_scale.json"
  }
}
```

---

## 6. API Plan

## 6.1. Tạo video job

```http
POST /api/v1/videos
```

Request:

```json
{
  "query": "How does the pH scale work?"
}
```

Response:

```json
{
  "id": "5e58f064-5c7c-4a8b-8a62-8dad2e8b68e6",
  "query": "How does the pH scale work?",
  "status": "queued",
  "current_stage": null,
  "progress": 0,
  "artifact_url": null,
  "created_at": "2026-08-01T04:00:00Z"
}
```

HTTP status:

```text
202 Accepted
```

Flow:

1. Validate query không rỗng.
2. Normalize query.
3. Tạo `video_jobs`.
4. Ghi `job_events` với `event_type = job_created`.
5. Đưa `job_id` vào queue.
6. Trả response.

---

## 6.2. Liệt kê video job

```http
GET /api/v1/videos
```

Query parameters đề xuất:

```text
status
concept_id
limit
offset
```

Response:

```json
{
  "items": [
    {
      "id": "uuid",
      "query": "How does the pH scale work?",
      "status": "completed",
      "progress": 100,
      "created_at": "2026-08-01T04:00:00Z",
      "completed_at": "2026-08-01T04:01:10Z"
    }
  ],
  "total": 1
}
```

---

## 6.3. Lấy chi tiết job

```http
GET /api/v1/videos/{job_id}
```

Response trong lúc chạy:

```json
{
  "id": "uuid",
  "query": "How does the pH scale work?",
  "concept": {
    "code": "ph_scale",
    "title": "How the pH Scale Works"
  },
  "status": "processing",
  "current_stage": "generating_visuals",
  "progress": 65,
  "retry_count": 1,
  "used_fallback": false,
  "estimated_cost_usd": 0.0012,
  "artifact_url": null,
  "error": null
}
```

Response khi thất bại:

```json
{
  "id": "uuid",
  "status": "failed",
  "current_stage": "rendering_video",
  "progress": 80,
  "error": {
    "code": "VIDEO_RENDER_FAILED",
    "message": "FFmpeg failed after retry."
  }
}
```

---

## 6.4. Lấy final video

```http
GET /api/v1/videos/{job_id}/artifact
```

Nếu job hoàn thành:

- Tìm `artifacts` với:
  - `job_id = requested job`
  - `artifact_type = final_video`
  - `status = ready`
- Trả `FileResponse`.

Nếu chưa hoàn thành:

```text
409 Conflict
```

```json
{
  "code": "ARTIFACT_NOT_READY",
  "status": "processing",
  "current_stage": "rendering_video"
}
```

Nếu job thất bại:

```text
422 Unprocessable Entity
```

---

## 6.5. Lấy job events

API này không bắt buộc nhưng hữu ích cho demo:

```http
GET /api/v1/videos/{job_id}/events
```

Dùng để hiển thị:

- State transition.
- Retry.
- Fallback.
- Artifact được tạo.
- Validation result.

---

## 7. Worker Pipeline

## 7.1. Worker Loop

Prototype dùng `asyncio.Queue`.

```python
class VideoWorker:
    def __init__(self, queue, pipeline):
        self.queue = queue
        self.pipeline = pipeline

    async def run(self):
        while True:
            job_id = await self.queue.get()

            try:
                await self.pipeline.execute(job_id)
            finally:
                self.queue.task_done()
```

Khởi động worker bằng FastAPI lifespan.

Demo chỉ chạy:

```text
1 worker
1 video job tại một thời điểm
```

Điều này tránh nhiều job render FFmpeg cùng lúc làm quá tải máy.

---

## 7.2. Pipeline Context

```python
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PipelineContext:
    job_id: str
    artifact_dir: Path

    concept: object | None = None
    lesson_plan: object | None = None
    scenes: list = field(default_factory=list)

    audio_artifacts: list = field(default_factory=list)
    visual_artifacts: list = field(default_factory=list)

    final_video_path: Path | None = None
```

Không lưu toàn bộ context vào database.

Database chỉ lưu state và metadata cần thiết.

---

## 7.3. Pipeline Orchestrator

```python
class VideoPipeline:
    async def execute(self, job_id: str):
        context = await self.create_context(job_id)

        try:
            await self.start_job(context)
            await self.resolve_concept(context)
            await self.plan_lesson(context)
            await self.validate_lesson(context)
            await self.generate_audio(context)
            await self.generate_visuals(context)
            await self.render_video(context)
            await self.validate_video(context)
            await self.complete_job(context)

        except PipelineError as exc:
            await self.fail_job(context, exc)

        except Exception as exc:
            await self.fail_job(
                context,
                PipelineError(
                    code="UNEXPECTED_PIPELINE_ERROR",
                    message=str(exc),
                ),
            )
```

---

## 8. Stage 1 — Resolve Concept

Cập nhật job:

```text
status = processing
current_stage = resolving_concept
progress = 5
started_at = now
```

Normalize query:

```python
def normalize_query(query: str) -> str:
    query = query.lower().strip()
    query = remove_punctuation(query)
    return collapse_whitespace(query)
```

Matching strategy:

1. Exact match với `canonical_query` đã normalize.
2. Keyword matching.
3. Nếu không match, fail job với `UNSUPPORTED_CONCEPT`.

Không dùng LLM cho stage này.

Sau khi match:

- Cập nhật `video_jobs.concept_id`.
- Ghi event `concept_resolved`.

---

## 9. Stage 2 — Plan Lesson

Cập nhật:

```text
current_stage = planning_lesson
progress = 15
```

Chiến lược:

```text
LLM generation
    ↓
Pydantic parse
    ↓
Rule validation
    ↓
Retry một lần nếu lỗi
    ↓
Curated template fallback
```

Lesson output cần có:

- `title`
- `summary`
- `learning_objectives`
- `estimated_duration_seconds`
- `scenes`

Nếu LLM thành công:

```text
lesson_plans.source = llm
```

Nếu không cấu hình LLM hoặc muốn demo hoàn toàn ổn định:

```text
lesson_plans.source = template
```

Nếu LLM lỗi và fallback:

```text
lesson_plans.source = fallback_template
video_jobs.used_fallback = true
```

Sau khi có lesson plan:

- Upsert `lesson_plans`.
- Xóa scene cũ nếu đang retry.
- Insert `lesson_scenes`.
- Ghi artifact loại `lesson_plan`.
- Ghi event `lesson_planned`.

---

## 10. Stage 3 — Validate Lesson

Cập nhật:

```text
current_stage = validating_lesson
progress = 25
```

Validation gồm:

### Schema checks

- Có từ 4 đến 8 scene.
- Mọi scene có narration.
- `scene_index` duy nhất.
- Duration scene hợp lệ.
- Visual type nằm trong allowlist.

### Content checks

- Lesson chứa các `required_facts`.
- Không để narration quá dài.
- Tổng thời lượng từ 45 đến 90 giây.
- Visual phù hợp với concept.

Nếu hợp lệ:

```text
lesson_plans.is_valid = true
lesson_plans.validation_errors = []
```

Nếu không hợp lệ:

- Retry lesson planner một lần.
- Nếu vẫn lỗi, dùng template fallback.
- Nếu template cũng lỗi, fail job với `INVALID_LESSON_PLAN`.

Ghi event:

```text
lesson_validated
lesson_validation_failed
fallback_used
```

---

## 11. Stage 4 — Generate Audio

Cập nhật:

```text
current_stage = generating_audio
progress = 40
```

Provider ban đầu:

```text
edge-tts
```

Flow từng scene:

1. Đọc `lesson_scenes.narration`.
2. Gọi TTS.
3. Lưu file:

```text
artifacts/{job_id}/audio/scene_01.mp3
```

4. Kiểm tra file tồn tại.
5. Dùng FFprobe đọc duration.
6. Cập nhật `lesson_scenes.actual_duration_seconds`.
7. Insert artifact `scene_audio`.

Retry:

```text
Attempt 1: voice mặc định
Attempt 2: retry cùng voice
Fallback: voice khác
```

Mọi retry được ghi trong `job_events`.

Nếu một scene vẫn không có audio sau fallback:

```text
AUDIO_GENERATION_FAILED
```

Progress cập nhật theo scene:

```text
40 + completed_scenes / total_scenes × 15
```

---

## 12. Stage 5 — Generate Visuals

Cập nhật:

```text
current_stage = generating_visuals
progress = 60
```

Không dùng text-to-video model cho demo.

Dùng programmatic renderer:

```text
title_card
ph_scale
electron_sharing
electron_transfer
comparison_table
summary_card
```

Flow:

1. Đọc `visual_type`.
2. Lấy renderer từ registry.
3. Render clip hoặc image sequence.
4. Lưu vào:

```text
artifacts/{job_id}/visuals/scene_01.mp4
```

5. Insert artifact `scene_visual`.

Fallback:

Nếu animation lỗi:

```text
dynamic renderer
    ↓
static slide renderer
```

Khi dùng static fallback:

```text
video_jobs.used_fallback = true
job_events.event_type = fallback_used
```

Nếu cả renderer chính và static fallback đều lỗi:

```text
VISUAL_GENERATION_FAILED
```

---

## 13. Stage 6 — Render Video

Cập nhật:

```text
current_stage = rendering_video
progress = 80
```

Video composer thực hiện:

1. Ghép visual và audio theo scene.
2. Căn scene duration theo audio.
3. Tạo subtitle.
4. Tạo transition.
5. Ghép toàn bộ scene.
6. Encode H.264 + AAC.
7. Xuất MP4.

Output:

```text
artifacts/{job_id}/video.mp4
```

Thông số demo:

```text
Resolution: 1280x720
FPS: 30
Video codec: H.264
Audio codec: AAC
Container: MP4
```

Insert artifact:

- `subtitle`
- `thumbnail`
- `final_video` với trạng thái ban đầu `pending`

Retry:

1. Render lần đầu ở 1280x720.
2. Nếu FFmpeg lỗi, retry một lần.
3. Có thể fallback xuống 854x480.
4. Nếu vẫn lỗi, fail `VIDEO_RENDER_FAILED`.

---

## 14. Stage 7 — Validate Video

Cập nhật:

```text
current_stage = validating_video
progress = 95
```

Dùng FFprobe kiểm tra:

- File tồn tại.
- File không rỗng.
- FFprobe đọc được.
- Có video stream.
- Có audio stream.
- Duration hợp lệ.
- Resolution hợp lệ.
- Video codec là H.264.
- Audio codec là AAC hoặc codec được hỗ trợ.

Lưu kết quả trong:

```text
artifacts.metadata
```

Ví dụ:

```json
{
  "ffprobe_readable": true,
  "has_video_stream": true,
  "has_audio_stream": true,
  "resolution": "1280x720",
  "video_codec": "h264",
  "audio_codec": "aac",
  "duration_valid": true
}
```

Nếu vượt qua validation:

```text
artifacts.status = ready
```

Nếu không hợp lệ:

```text
artifacts.status = invalid
```

Sau một lần render retry mà vẫn lỗi:

```text
INVALID_VIDEO_ARTIFACT
```

---

## 15. Complete Job

Khi final video hợp lệ:

```text
video_jobs.status = completed
video_jobs.current_stage = validating_video
video_jobs.progress = 100
video_jobs.completed_at = now
video_jobs.error_code = null
video_jobs.error_message = null
```

Ghi event:

```text
job_completed
```

API có thể tạo artifact URL động:

```text
/api/v1/videos/{job_id}/artifact
```

Không cần lưu URL trong database.

---

## 16. Fail Job

Khi pipeline không thể tiếp tục:

```text
video_jobs.status = failed
video_jobs.error_code = pipeline_error.code
video_jobs.error_message = pipeline_error.message
video_jobs.updated_at = now
```

Ghi event:

```json
{
  "event_type": "job_failed",
  "stage": "rendering_video",
  "message": "FFmpeg failed after retry.",
  "metadata": {
    "error_code": "VIDEO_RENDER_FAILED"
  }
}
```

Không xóa intermediate artifact để phục vụ debug.

---

## 17. Progress Mapping

```python
PROGRESS_BY_STAGE = {
    "resolving_concept": 5,
    "planning_lesson": 15,
    "validating_lesson": 25,
    "generating_audio": 40,
    "generating_visuals": 60,
    "rendering_video": 80,
    "validating_video": 95,
}
```

Khi hoàn thành:

```text
progress = 100
```

---

## 18. Retry và Fallback Matrix

| Stage | Retry | Fallback | Error cuối |
|---|---:|---|---|
| Resolve concept | 0 | Không | `UNSUPPORTED_CONCEPT` |
| Plan lesson | 1 | Curated template | `LESSON_PLANNING_FAILED` |
| Validate lesson | 1 | Curated template | `INVALID_LESSON_PLAN` |
| Generate audio | 1 mỗi scene | Voice khác | `AUDIO_GENERATION_FAILED` |
| Generate visuals | 1 mỗi scene | Static visual | `VISUAL_GENERATION_FAILED` |
| Render video | 1 | Độ phân giải thấp hơn | `VIDEO_RENDER_FAILED` |
| Validate video | 1 render lại | Không | `INVALID_VIDEO_ARTIFACT` |

Mỗi retry:

- Tăng `video_jobs.retry_count`.
- Ghi một `job_events`.
- Không tạo bảng attempt riêng.

---

## 19. Artifact Directory

```text
artifacts/
└── {job_id}/
    ├── lesson_plan.json
    ├── audio/
    │   ├── scene_01.mp3
    │   ├── scene_02.mp3
    │   └── scene_03.mp3
    ├── visuals/
    │   ├── scene_01.mp4
    │   ├── scene_02.mp4
    │   └── scene_03.mp4
    ├── subtitles/
    │   └── captions.srt
    ├── thumbnail.png
    └── video.mp4
```

Tên file phải deterministic để dễ retry và resume.

---

## 20. Idempotency

Trước khi tạo artifact, worker kiểm tra:

1. Database đã có artifact `ready` chưa.
2. File có tồn tại không.
3. File có vượt qua validation tối thiểu không.

Ví dụ:

```python
audio_artifact = await artifact_repository.find_scene_artifact(
    scene_id=scene.id,
    artifact_type="scene_audio",
)

if audio_artifact and audio_artifact.status == "ready":
    if Path(audio_artifact.file_path).exists():
        skip_generation()
```

Nếu database nói `ready` nhưng file không tồn tại:

- Đánh dấu artifact `invalid`.
- Sinh lại file.
- Ghi event `artifact_missing`.

---

## 21. Migration Plan

Dùng:

```text
SQLAlchemy 2
Alembic
PostgreSQL
```

Migration đầu tiên tạo:

- Enum.
- 6 bảng.
- Foreign key.
- Index.

Migration thứ hai seed ba supported concepts.

Hoặc seed bằng command riêng:

```bash
python -m app.scripts.seed_concepts
```

Khuyến nghị seed bằng script để có thể chạy lại an toàn.

Seed phải dùng upsert theo `supported_concepts.code`.

---

## 22. Repository Plan

### SupportedConceptRepository

```python
get_by_id()
get_by_code()
list_active()
find_by_normalized_query()
```

### VideoJobRepository

```python
create()
get_by_id()
list()
update_status()
update_progress()
mark_completed()
mark_failed()
increment_retry()
set_fallback_used()
```

### LessonRepository

```python
upsert_plan()
replace_scenes()
get_plan_by_job()
get_scenes_by_job()
update_scene_actual_duration()
```

### ArtifactRepository

```python
create()
get_by_id()
list_by_job()
find_final_video()
find_scene_artifact()
mark_ready()
mark_invalid()
```

### JobEventRepository

```python
create()
list_by_job()
```

---

## 23. Transaction Boundaries

Không giữ database transaction mở trong lúc gọi LLM, TTS hoặc FFmpeg.

Flow đúng:

```text
Mở transaction
→ cập nhật job stage
→ commit

Gọi provider hoặc render file

Mở transaction mới
→ lưu result hoặc error
→ commit
```

Lesson plan và scene nên được ghi trong cùng một transaction:

```text
upsert lesson plan
delete old scenes
insert new scenes
commit
```

Final artifact validation và complete job cũng nên nằm trong một transaction:

```text
mark final artifact ready
mark job completed
create job_completed event
commit
```

---

## 24. Error Codes

```text
JOB_NOT_FOUND
UNSUPPORTED_CONCEPT
LESSON_PLANNING_FAILED
INVALID_LESSON_PLAN
AUDIO_GENERATION_FAILED
VISUAL_GENERATION_FAILED
VIDEO_RENDER_FAILED
INVALID_VIDEO_ARTIFACT
ARTIFACT_NOT_READY
ARTIFACT_FILE_MISSING
UNEXPECTED_PIPELINE_ERROR
```

Error code phải ổn định để test và client xử lý.

Error message có thể chi tiết hơn nhưng không được chứa API key hoặc secret.

---

## 25. Logging

Mỗi log cần có:

```text
job_id
stage
scene_index nếu có
provider nếu có
attempt nếu có
duration_ms nếu có
```

Ví dụ:

```text
INFO job_id=123 stage=planning_lesson source=llm
WARNING job_id=123 stage=planning_lesson validation_failed=true
INFO job_id=123 stage=planning_lesson fallback=ph_scale.json
INFO job_id=123 stage=generating_audio scene_index=2 provider=edge_tts
INFO job_id=123 stage=rendering_video resolution=1280x720
INFO job_id=123 stage=validating_video result=passed
```

`job_events` dùng cho audit nghiệp vụ.

Application log dùng cho debug kỹ thuật.

---

## 26. Test Plan

## 26.1. Unit Tests

### Concept Resolver

- Map đúng ba query bắt buộc.
- Query khác hoa thường vẫn map đúng.
- Query có dấu câu vẫn map đúng.
- Query không hỗ trợ trả `UNSUPPORTED_CONCEPT`.

### Lesson Validator

- Reject lesson không có scene.
- Reject narration rỗng.
- Reject visual type ngoài allowlist.
- Reject lesson thiếu required fact.
- Accept curated template.

### Job State

- Job mới có status `queued`.
- Worker start chuyển sang `processing`.
- Complete đặt progress bằng 100.
- Fail lưu error code và message.

### Artifact Validation

- Reject file không tồn tại.
- Reject MP4 thiếu audio stream.
- Accept MP4 hợp lệ.
- Metadata FFprobe được lưu đúng.

---

## 26.2. Repository Tests

- Tạo và đọc video job.
- Lọc job theo status.
- Upsert lesson plan.
- Replace scene trong transaction.
- Tìm final video.
- Timeline event đúng thứ tự.

Dùng PostgreSQL test database hoặc Testcontainers nếu phù hợp.

---

## 26.3. Integration Tests

Flow:

```text
POST /videos
→ nhận 202
→ worker xử lý
→ poll GET /videos/{id}
→ status completed
→ GET artifact trả video/mp4
```

Test cả ba query bắt buộc.

---

## 26.4. Failure Tests

Mock:

- LLM trả JSON lỗi.
- TTS timeout.
- Renderer ném exception.
- FFmpeg exit code khác 0.
- FFprobe không đọc được file.
- File artifact bị xóa sau khi database đánh dấu ready.

Kiểm tra:

- Retry count.
- used_fallback.
- job_events.
- error code cuối cùng.
- Không có job treo ở `processing`.

---

## 26.5. Reliability Tests

Chạy:

```text
3 concepts × 3 runs = 9 jobs
```

Mục tiêu:

```text
9/9 job hoàn thành
0 final video invalid
0 job bị treo
Fallback hoạt động khi LLM hoặc renderer bị mock lỗi
```

Báo cáo:

- Tổng thời gian.
- Thời gian trung bình.
- Số retry.
- Số fallback.
- Chi phí ước tính.
- Thời lượng video.
- Kích thước video.

---

## 27. Implementation Phases

## Phase 1 — Database và Migration

- Cài SQLAlchemy, Alembic và PostgreSQL driver.
- Tạo enum.
- Tạo 6 model.
- Tạo repository.
- Seed 3 concept.
- Viết repository tests.

Kết quả:

```text
Database hoạt động
Concept được seed
CRUD job hoạt động
```

---

## Phase 2 — API và Job Lifecycle

- POST tạo job.
- GET list job.
- GET job detail.
- GET job events.
- Async queue.
- Worker mock.
- Progress mock.

Kết quả:

```text
POST
→ queued
→ processing
→ completed
```

Chưa tạo video thật.

---

## Phase 3 — Lesson Plan

- Concept resolver.
- Curated templates.
- Lesson schema.
- Lesson validator.
- Lưu lesson plan và scene.
- Tạo lesson_plan artifact.

Kết quả:

```text
Query
→ concept
→ lesson plan
→ scenes
```

---

## Phase 4 — Audio

- Edge TTS provider.
- Tạo audio từng scene.
- FFprobe audio.
- Artifact metadata.
- Retry và fallback voice.

Kết quả:

```text
scene narration
→ scene audio
```

---

## Phase 5 — Visual

- Renderer registry.
- Title card.
- pH scale.
- Electron sharing.
- Electron transfer.
- Comparison table.
- Summary card.
- Static fallback.

Kết quả:

```text
scene visual_data
→ scene visual clip
```

---

## Phase 6 — Video Composition

- Subtitle generation.
- Scene composition.
- Final video render.
- Thumbnail.
- Final video artifact.

Kết quả:

```text
audio + visual + subtitle
→ video.mp4
```

---

## Phase 7 — Validation và Reliability

- FFprobe final video.
- Artifact metadata validation.
- Retry render.
- Failure states.
- 9-run reliability test.
- Cost estimate.

Kết quả:

```text
completed chỉ khi final video hợp lệ
```

---

## 28. Definition of Done

Demo hoàn thành khi:

- PostgreSQL chứa đúng 6 bảng.
- Ba supported concepts được seed.
- API tạo job trả `202`.
- Worker xử lý job bất đồng bộ.
- Client xem được status, stage và progress.
- Cả ba query bắt buộc chạy end-to-end.
- Lesson plan và scene được lưu trong database.
- Audio và visual được tạo cho từng scene.
- Final video có cả hình ảnh và âm thanh.
- Artifact metadata được lưu.
- FFprobe validation được lưu trong `artifacts.metadata`.
- Client tải hoặc mở được final video.
- Retry được ghi trong `job_events`.
- Fallback được ghi trong `job_events`.
- Job lỗi có error code rõ ràng.
- Không có job bị treo ở trạng thái processing.
- Chạy 9 reliability jobs không tạo final artifact hỏng.

---

## 29. Nguyên tắc thiết kế

```text
Database nhỏ
+ Pipeline rõ ràng
+ Artifact local
+ Deterministic fallback
+ Validation bắt buộc
+ Event history đủ dùng
```

Schema demo không cố mô phỏng đầy đủ production.

Mục tiêu là chứng minh:

- API rõ ràng.
- Worker lifecycle đúng.
- Pipeline AI có validation.
- Retry và fallback có chủ đích.
- Video artifact thực sự được tạo.
- Kiến trúc có thể mở rộng sau demo.
