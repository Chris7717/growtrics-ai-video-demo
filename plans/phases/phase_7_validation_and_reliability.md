# Phase 7: Validation và Reliability

## Mục tiêu
Xác thực sản phẩm cuối cùng (MP4 video) đảm bảo không bị hỏng file, hoàn tất quy trình job hoặc xử lý các fail-state hệ thống một cách trơn tru. Đảm bảo tính ổn định của toàn bộ Worker thông qua kiểm thử E2E.

## Các bước chi tiết

### Step 7.1: Final Video Validation (Stage 7)
- Cập nhật `video_jobs` (`current_stage = validating_video`, `progress = 95`).
- Viết `app/pipeline/video_validator.py`.
- Gọi FFprobe để kiểm tra file final video:
  - File có tồn tại, kích thước > 0.
  - Có Video stream codec `H.264`.
  - Có Audio stream codec `AAC`.
  - Độ dài (duration) và độ phân giải đúng chuẩn (1280x720).
- Cập nhật trường `metadata` trong `artifacts` dạng JSON báo cáo kết quả check, chuyển `status = ready` nếu Pass, hoặc `invalid` nếu hỏng.

### Step 7.2: Completion & Failure Handling
- **Job Hoàn Thành**:
  - Gắn `video_jobs.status = completed`, `progress = 100`, xoá `error_code`, `error_message`.
  - Bắn event `job_completed`.
- **Job Thất Bại**:
  - Khi pipeline bắt được `PipelineError`, cập nhật `video_jobs.status = failed` kèm `error_code` và `error_message`.
  - Event `job_failed`.
- Đảm bảo cơ chế Idempotency: skip creation steps nếu các artifact đã tồn tại và ở trạng thái `ready`.

### Step 7.3: Integration & Reliability Tests
- Viết kịch bản test để đảm bảo:
  - `POST /videos` thành công.
  - Background worker xử lý end-to-end cho ra file video không lỗi.
  - Không có job nào bị treo vô hạn ở state `processing`.
- E2E Test với Reliability mock: 3 concepts x 3 lần chạy (9 jobs) mô phỏng lỗi ngẫu nhiên để verify tính năng Fallback / Retry hoạt động bình thường, không làm gián đoạn Worker queue chính.
