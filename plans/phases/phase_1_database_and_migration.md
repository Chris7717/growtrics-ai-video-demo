# Phase 1: Database và Migration

## Mục tiêu
Thiết lập cấu trúc thư mục, cấu hình database, tạo các schema cơ bản (BaseDTO) và các model database (PostgreSQL) thông qua SQLAlchemy và Alembic. Thực hiện seed dữ liệu mẫu cho các concept.

## Các bước chi tiết

### Step 1.1: Project Setup & Core Configuration
- Tạo cấu trúc thư mục chuẩn: `app/api`, `app/db/models`, `app/schemas`, `app/services`, `app/repositories`, `app/queue`, `app/scripts`.
- Cấu hình file `app/config.py` bằng `pydantic-settings` để quản lý `DATABASE_URL` và các biến môi trường khác.

### Step 1.2: Định nghĩa Base Schema & Enums (Theo rules)
- Tạo `app/schemas/base.py`:
  - Định nghĩa lớp `BaseDTO` kế thừa từ `pydantic.BaseModel`.
  - Bật cấu hình `from_attributes = True` để dễ dàng map từ model SQLAlchemy.
- Tạo `app/db/enums.py`:
  - `JobStatus`: `queued`, `processing`, `completed`, `failed`.
  - `JobStage`: `resolving_concept`, `planning_lesson`, `validating_lesson`, `generating_audio`, `generating_visuals`, `rendering_video`, `validating_video`.
  - `ArtifactType`: `lesson_plan`, `scene_audio`, `scene_visual`, `subtitle`, `thumbnail`, `final_video`.
  - `ArtifactStatus`: `pending`, `ready`, `invalid`.

### Step 1.3: Database Models
- Tạo `app/db/base.py` chứa `Base` của SQLAlchemy.
- Tạo `app/db/session.py` với `async_sessionmaker` và `create_async_engine`.
- Định nghĩa 6 bảng trong `app/db/models/`:
  - `supported_concepts.py`
  - `video_jobs.py` (cần chứa các metadata lỗi, tiến độ)
  - `lesson_plans.py`
  - `lesson_scenes.py`
  - `artifacts.py`
  - `job_events.py`

### Step 1.4: Alembic Migrations
- Khởi tạo thư mục alembic bằng lệnh `alembic init -t async migrations`.
- Sửa `migrations/env.py` để import toàn bộ model và kết nối bằng AsyncEngine.
- Tạo revision đầu tiên: `alembic revision --autogenerate -m "Initial tables"`.
- Áp dụng migration: `alembic upgrade head`.

### Step 1.5: Seeding Data
- Tạo script `app/scripts/seed_concepts.py` để insert 3 bản ghi vào `supported_concepts`:
  1. `ph_scale`
  2. `covalent_bonds`
  3. `ionic_vs_covalent`
- Dùng `upsert` (INSERT ON CONFLICT) dựa trên `code` để tránh trùng lặp khi chạy lại.

### Step 1.6: Repositories (CRUD)
- Xây dựng các class Repository xử lý database (Không mapping thủ công mà dùng DTO unpacking như `fastapi-backend-rules.md` yêu cầu):
  - `SupportedConceptRepository`
  - `VideoJobRepository`
  - `LessonRepository`
  - `ArtifactRepository`
  - `JobEventRepository`
- Viết unit test cho repository sử dụng pytest và SQLite in-memory hoặc Testcontainers.
