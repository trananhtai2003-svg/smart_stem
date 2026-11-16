# SMART STEM 2.1.3 – QR LAN FIX

- Tự dò IPv4 LAN của máy chủ qua `/api/network-info`.
- Tự điền địa chỉ gợi ý vào ô tạo QR.
- Từ chối tạo QR bằng localhost/127.0.0.1/0.0.0.0.
- Khi mở trang quản trị, nếu có thiết bị chưa có QR, hệ thống tự tạo QR cho các thiết bị hiện có.

## Dùng thử
1. Giải nén vào thư mục mới.
2. Chạy START_SMART_STEM.bat.
3. Mở dashboard trên máy giáo viên.
4. Đảm bảo điện thoại và máy tính cùng Wi-Fi/LAN.
5. Kiểm tra IP gợi ý, nhấn Tạo QR toàn bộ thiết bị.
6. Quét thử một mã bằng điện thoại.

Nếu điện thoại không mở được trang: cho phép Python qua Windows Defender Firewall (Private networks), kiểm tra máy tính và điện thoại cùng mạng, không bật Wi-Fi Guest/AP isolation.
QR nội bộ chỉ dùng được trong mạng LAN. Muốn quét ngoài trường cần cấu hình hosting/domain/HTTPS riêng.
