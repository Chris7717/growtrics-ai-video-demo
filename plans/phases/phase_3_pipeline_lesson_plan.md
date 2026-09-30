# Phase 3: Lesson Plan Pipeline

## Mục tiêu
Tích hợp luồng AI xử lý câu hỏi ban đầu, xác định chủ đề, và tạo ra kịch bản giảng dạy (Lesson Plan) bao gồm các phân cảnh (Scenes). Sử dụng fallback/template để mô phỏng LLM nếu cần thiết.

## Các bước chi tiết

### Step 3.1: Pipeline Orchestrator Skeleton
- Tạo `app/pipeline/orchestrator.py` (`VideoPipeline`).
- Tạo dataclass `PipelineContext` để chia sẻ dữ liệu trung gian (`app/workers/pipeline_context.py`).
- Quản lý Transaction boundaries: Mở transaction để cập nhật stage của Job, sau đó commit. Gọi logic bên ngoài, rồi mở lại transaction ghi kết quả.

### Step 3.2: Concept Resolver (Stage 1)
- Xây dựng `app/pipeline/concept_resolver.py`.
- Logic: Normalize `query` (xóa dấu câu, viết thường) và match với `canonical_query` trong database.
- Cập nhật `video_jobs` (`current_stage = resolving_concept`, `progress = 5`).
- Ghi `job_events` (event_type: `concept_resolved`).
- Ném exception `UNSUPPORTED_CONCEPT` nếu không khớp concept nào.

### Step 3.3: Lesson Planner (Stage 2)
- Cập nhật `video_jobs` (`current_stage = planning_lesson`, `progress = 15`).
- Xây dựng `app/pipeline/lesson_planner.py`.
- Nếu có Gemini provider, gửi request kèm json_schema mong muốn.
- Tích hợp Curated Template: đọc nội dung từ file json (vd: `app/templates/ph_scale.json`) khi request LLM lỗi hoặc dùng làm fallback cố định cho demo.

### Step 3.4: Lesson Validator & Database Write (Stage 3)
- Cập nhật `video_jobs` (`current_stage = validating_lesson`, `progress = 25`).
- Xây dựng `app/pipeline/lesson_validator.py`.
- Validate số lượng cảnh (4-8 scenes), độ dài chữ trong mỗi cảnh, và visual types có hợp lệ theo allowlist hay không.
- Nếu hợp lệ:
  - Lưu `lesson_plans` và `lesson_scenes` vào database chung 1 Transaction.
  - Tạo một artifact record cho `lesson_plan`.
  - Ghi sự kiện `lesson_planned`.
- Nếu không hợp lệ: retry, ghi event `fallback_used` nếu rơi vào template, hoặc ném lỗi `INVALID_LESSON_PLAN`.
