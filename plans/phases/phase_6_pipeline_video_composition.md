# Phase 6: Video Composition Pipeline

## Mục tiêu
Ghép tất cả các mảnh ghép audio, visual của từng scene thành 1 file MP4 video hoàn chỉnh, tạo subtitle, thumbnail và cập nhật DB.

## Các bước chi tiết

### Step 6.1: Subtitle Generation
- Cập nhật `video_jobs` (`current_stage = rendering_video`, `progress = 80`).
- Dựa trên mảng `lesson_scenes.narration` và độ dài thời gian, tạo một file subtitle chuẩn SRT `artifacts/{job_id}/subtitles/captions.srt`.
- Lưu DB `artifacts` (loại `subtitle`).

### Step 6.2: Final Video Composer (Stage 6)
- Xây dựng `app/pipeline/video_composer.py`.
- Dùng thư viện `MoviePy` hoặc subprocess gọi thẳng dòng lệnh `ffmpeg`.
- Yêu cầu FFmpeg:
  - Nối các scene (visual + audio) theo đúng thứ tự.
  - Thông số render: `Resolution: 1280x720`, `FPS: 30`, `Video Codec: H.264`, `Audio Codec: AAC`.
- Lưu trữ kết quả ở `artifacts/{job_id}/video.mp4`.

### Step 6.3: Thumbnail Generation
- Trích xuất 1 khung hình từ video (vd: ở mốc thời gian giữa hoặc giây đầu tiên của scene chính) bằng FFmpeg.
- Lưu thành file `artifacts/{job_id}/thumbnail.png`.
- Ghi DB bảng `artifacts`.

### Step 6.4: Quản lý Artifact trạng thái chờ
- Bản ghi `artifacts` cho video cuối phải khởi tạo trạng thái `pending` trước khi nhảy sang bước Validation tiếp theo.
- Xử lý cơ chế Retry render lần 2 (với độ phân giải `854x480`) nếu render lần đầu bị lỗi. Bắn event `VIDEO_RENDER_FAILED` nếu vẫn hỏng.
