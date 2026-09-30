# Phase 4: Audio Generation Pipeline

## Mục tiêu
Dịch kịch bản văn bản (narration) của từng phân cảnh (scene) thành giọng nói (audio/mp3) bằng Text-to-Speech, và lưu trữ artifact.

## Các bước chi tiết

### Step 4.1: TTS Provider
- Tạo interface `app/providers/tts/interface.py`.
- Implement `EdgeTTSProvider` (`app/providers/tts/edge_tts_provider.py`) sử dụng thư viện `edge-tts` (do chi phí thấp và dễ demo).

### Step 4.2: Audio Generator (Stage 4)
- Cập nhật `video_jobs` (`current_stage = generating_audio`, `progress = 40`).
- Xây dựng `app/pipeline/audio_generator.py`.
- Vòng lặp quét qua từng scene trong `PipelineContext.scenes`:
  - Gọi TTS Provider sinh file âm thanh.
  - Lưu file thực tế vào thư mục `artifacts/{job_id}/audio/scene_{index}.mp3`.

### Step 4.3: Audio Validation & Metadata
- Sau khi file tạo thành công, dùng module python `ffprobe` để lấy độ dài thực tế của file âm thanh (tính bằng giây).
- Update trường `actual_duration_seconds` trong bảng `lesson_scenes`.
- Ghi log database bảng `artifacts` (loại `scene_audio`) và gán trạng thái `ready`.
- Tính toán progress update sau mỗi scene (`40 + (completed / total) * 15`).

### Step 4.4: Retry & Fallback
- Nếu call TTS provider thất bại, tiến hành retry 1 lần cho cảnh đó.
- Thử thay đổi Voice nếu cần thiết (fallback voice).
- Ghi nhận `job_events` cho mỗi lần retry (`TTS_TIMEOUT`, `event_type = retry`).
- Nếu thất bại toàn bộ, ném lỗi `AUDIO_GENERATION_FAILED`.
