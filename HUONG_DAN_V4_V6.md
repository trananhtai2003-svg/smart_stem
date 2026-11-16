# HƯỚNG DẪN SMART STEM 2.1 – QR LEARNING

## 1. Vận hành trên máy giáo viên
- Chạy `START_SMART_STEM.bat`.
- Mở `http://127.0.0.1:8000`.
- Để điện thoại truy cập, lấy IPv4 máy chủ bằng lệnh `ipconfig`.

## 2. Tạo và in QR
- Nhập địa chỉ điện thoại có thể truy cập, ví dụ `http://192.168.1.10:8000`.
- Chọn **Tạo QR toàn bộ thiết bị**.
- Chọn **Tải bộ QR dạng ZIP**, giải nén và in từng ảnh PNG.
- Dán QR tương ứng lên CPU, RAM, Mainboard, HDD, Modem, Router, Media Converter và Card mạng.

## 3. Học sinh sử dụng
1. Mở camera điện thoại và quét QR.
2. Đọc thông tin thiết bị.
3. Xem video và mô hình 3D/AR.
4. Làm câu hỏi trắc nghiệm nhanh.
Không cần đăng nhập hoặc nhập bất kỳ thông tin cá nhân nào.

## 4. Báo cáo
Mở **Thống kê & báo cáo** để xem lượt quét, lượt trả lời, số câu đúng và tỷ lệ đúng theo thiết bị. Có thể xuất CSV để mở bằng Excel.

## 5. Giới hạn và lưu ý
- Dữ liệu thống kê là ẩn danh, không xác định được học sinh cụ thể.
- Điện thoại phải truy cập được IP máy chủ; không dùng localhost trong QR.
- Đổi IP máy chủ thì cần tạo lại QR.
- AR phụ thuộc thiết bị và trình duyệt; 3D/AR cần tải thư viện từ CDN ở lần đầu.
- Không mở máy chủ chưa có xác thực ra Internet.
- Sao lưu `data/smart_stem.db` trước mọi lần nâng cấp.
