# Phase 5: Visual Generation Pipeline

## Mục tiêu
Tạo ra các video/ảnh động minh hoạ (visuals) phù hợp với kịch bản của từng scene dựa trên các programmatic renderers thay vì AI Text-to-Video.

## Các bước chi tiết

### Step 5.1: Renderer Registry & Kiến trúc
- Xây dựng class `RendererRegistry` trong `app/renderers/registry.py` để map các `visual_type` (như `title_card`, `ph_scale`) với class sinh hình tương ứng.
- Viết base interface cho các renderer với input là `visual_data` JSON và output là đường dẫn tới file video mp4 hoặc hình ảnh jpeg.

### Step 5.2: Triển khai các Renderers cụ thể
- Cập nhật `video_jobs` (`current_stage = generating_visuals`, `progress = 60`).
- Implement các file riêng biệt:
  - `app/renderers/title_card.py`
  - `app/renderers/ph_scale.py`
  - `app/renderers/electron_sharing.py`
  - `app/renderers/electron_transfer.py`
  - `app/renderers/comparison_table.py`
  - `app/renderers/summary_card.py`
- Có thể dùng thư viện `MoviePy`, `Pillow` hoặc `matplotlib` để render thành clip dài bằng với duration của audio cảnh đó.

### Step 5.3: Visual Orchestration & Artifacts (Stage 5)
- Viết `app/pipeline/visual_generator.py` duyệt qua từng scene.
- Load loại hình đồ hoạ theo field `visual_type` để gọi renderer tương ứng.
- Lưu file đầu ra tại `artifacts/{job_id}/visuals/scene_{index}.mp4`.
- Tạo record `artifacts` loại `scene_visual` trong db.

### Step 5.4: Static Slide Fallback
- Nếu việc render video/animation lỗi, tự động chuyển về chế độ "Static Fallback" (chỉ tạo 1 khung hình tĩnh thay vì video động).
- Update DB job cờ `used_fallback = true` và ghi sự kiện `fallback_used`.
- Ném lỗi `VISUAL_GENERATION_FAILED` nếu cả renderer chính và static fallback đều lỗi.
