# SMART STEM V2.6 – BỔ SUNG XÓA THIẾT BỊ

## Cách sử dụng
1. Mở trang quản trị SMART STEM.
2. Tìm thiết bị cần xóa trong danh sách.
3. Nhấn **Xóa** ở cột thao tác.
4. Đọc hộp thoại xác nhận; chỉ xác nhận khi đúng mã và tên thiết bị.

## Quy tắc dữ liệu
- API xóa thiết bị sử dụng endpoint `DELETE /api/devices/{code}` đã có trong backend.
- Bản ghi thiết bị bị xóa khỏi danh sách quản trị và trang QR tương ứng không còn hoạt động.
- Lịch sử `device_events` được giữ nguyên để không làm mất dữ liệu thống kê cũ.
- Ảnh QR và tệp media không tự động xóa; chúng được giữ lại để tránh xóa nhầm tài nguyên dùng chung và hỗ trợ khôi phục thủ công.
- Việc xóa thiết bị không xóa mô-đun chứa thiết bị.

## Khuyến nghị
Sao lưu thư mục `data` và `storage` trước khi xóa số lượng lớn thiết bị. Nếu cần khôi phục một thiết bị đã xóa, hãy tạo lại thiết bị với cùng mã và cấu hình lại liên kết media/QR.
