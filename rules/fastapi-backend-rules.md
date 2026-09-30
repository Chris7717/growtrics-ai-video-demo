# FastAPI Backend Development Rules

Tài liệu này quy định các quy tắc và tiêu chuẩn cốt lõi khi xây dựng backend bằng FastAPI. Tất cả các lập trình viên cần tuân thủ để đảm bảo tính nhất quán, dễ bảo trì và chất lượng mã nguồn của dự án.

## 1. Kế thừa `BaseDTO`
- **Sử dụng `BaseDTO`**: Tất cả các DTO (Data Transfer Object / Pydantic models) phải được kế thừa từ một lớp `BaseDTO` chung.
- **Metadata chung**: `BaseDTO` sẽ chứa các metadata cần thiết (ví dụ: cấu hình model, các trường chung như `created_at`, `updated_at`, hoặc audit logic) để các DTO con có thể tái sử dụng.
- **Lợi ích**: Đảm bảo cấu trúc dữ liệu đồng nhất và giảm thiểu code lặp lại.

## 2. Tài liệu Swagger đầy đủ
- **Controllers (Endpoints)**: Mỗi API endpoint (router) phải được khai báo đầy đủ các tham số như `summary`, `description`, `response_model`, `status_code`, và `tags`.
- **DTOs**: Mọi trường dữ liệu trong DTO phải sử dụng `Field(...)` của Pydantic để cung cấp `description`, `example`, và các ràng buộc dữ liệu (validation).
- **Lợi ích**: Swagger UI là tài liệu chính để Frontend và client tích hợp. Việc document chi tiết giúp giảm thiểu giao tiếp không cần thiết và lỗi tích hợp.

## 3. Không dùng chuỗi/số raw (Sử dụng Enum)
- **Không dùng Magic Values**: Hạn chế tối đa việc hardcode các chuỗi (string) hoặc số (number) trực tiếp trong logic code (ví dụ: trạng thái đơn hàng, loại người dùng, mã lỗi...).
- **Tạo Enum trong Config/Constants**: Hãy định nghĩa các giá trị này dưới dạng `Enum` trong thư mục cấu hình (config) hoặc hằng số (constants) và import vào để sử dụng.
- **Lợi ích**: Tránh lỗi type/chính tả, dễ dàng tìm kiếm/thay thế và đồng bộ giá trị trên toàn hệ thống.

## 4. Gán giá trị bằng DTO, không mapping từng trường
- **Sử dụng DTO unpacking**: Ở tầng Controller và Service, KHÔNG mapping/gán từng trường một cách thủ công. Hãy tận dụng DTO để gán giá trị (ví dụ: dùng unpacking `**`).
  - ❌ *Không tốt*: `User(name=dto.name, age=dto.age, email=dto.email)`
  - ✅ *Tốt*: `User(**dto.model_dump())` (hoặc `**dto.dict()` đối với Pydantic v1)
- **Lợi ích**: Code ngắn gọn, sạch sẽ hơn và tự động tương thích khi model DTO có sự thay đổi thêm/bớt trường dữ liệu.

## 5. Message cụ thể cho từng trạng thái API
- **Phản hồi rõ ràng**: Các API khi trả về kết quả (dù thành công hay lỗi) ứng với các trạng thái (HTTP status codes) hoặc logic khác nhau phải luôn kèm theo một `message` cụ thể, riêng biệt và mang ý nghĩa mô tả rõ tình huống đó.
- **Tránh dùng từ chung chung**: Không sử dụng các thông báo như "Success" hay "Error" chung chung. Thay vào đó hãy trả về các câu như "Tạo người dùng thành công", "Không tìm thấy thông tin tài khoản", "Mật khẩu không chính xác".
- **Lợi ích**: Giúp frontend dễ dàng xử lý thông báo hiển thị cho end-user và tiết kiệm thời gian khi debug các lỗi từ server.
