# Phase 2: API và Job Lifecycle

## Mục tiêu
Xây dựng các API cơ bản để nhận request từ Client, lưu vào database, tạo Job cho worker, và truy xuất tiến độ của video job. Thiết lập khung sườn cho Worker xử lý bất đồng bộ.

## Các bước chi tiết

### Step 2.1: Khai báo API Schemas (DTOs)
- Tạo file `app/schemas/video_requests.py` và `app/schemas/video_responses.py`.
- Các request/response model (`VideoJobRequest`, `VideoJobResponse`, `VideoJobDetailResponse`) phải kế thừa từ `BaseDTO`.
- Áp dụng triệt để `Field(..., description="...", example="...")` cho Swagger Documentation.

### Step 2.2: Khởi tạo Async Queue & Worker Skeleton
- Tạo `app/queue/interface.py` và `app/queue/asyncio_queue.py` mô phỏng queue bằng `asyncio.Queue`.
- Viết khung class `VideoWorker(queue, pipeline)` trong `app/workers/video_worker.py`.
- Khởi tạo background task trong FastAPI lifespan tại `app/main.py` để chạy worker ngầm khi server khởi động.

### Step 2.3: API Endpoints (Controllers)
- Tạo `app/api/videos.py` router và mount vào `app/api/router.py`.
- `POST /api/v1/videos`:
  - Validate payload (query).
  - Khởi tạo job mới với `status=queued` qua `VideoJobService`.
  - Gửi `job_id` vào `asyncio.Queue`.
  - Trả về `202 Accepted` kèm message cụ thể (VD: "Đã đưa yêu cầu tạo video vào hàng đợi").
- `GET /api/v1/videos`:
  - Trả về danh sách jobs (phân trang, filter theo status).
- `GET /api/v1/videos/{job_id}`:
  - Lấy chi tiết job bao gồm state, tiến độ (`progress`), stage hiện tại.
- `GET /api/v1/videos/{job_id}/events` (Tuỳ chọn để demo):
  - Lấy lịch sử log của job.
- `GET /api/v1/videos/{job_id}/artifact`:
  - Logic tải hoặc stream video cuối cùng, trả về HTTP 409 nếu trạng thái là chưa sẵn sàng (`ARTIFACT_NOT_READY`).

### Step 2.4: Integration Tests cho API
- Sử dụng `httpx.AsyncClient` và `pytest.fixture` để gọi các endpoint API.
- Đảm bảo logic API, HTTP codes (`202`, `409`, `422`, `404`), format lỗi đáp ứng đúng các quy tắc.
