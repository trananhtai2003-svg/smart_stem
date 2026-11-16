# SMART COMPUTER & NETWORK STEM 2.2 – QR LEARNING

## Mục tiêu phiên bản
Bản 2.2 tập trung vào học liệu có nguồn gốc rõ ràng và trang học tập QR. Không còn phần ESP32.

## Nội dung tư liệu đã tích hợp
1. Mainboard: bảng chú thích do giáo viên cung cấp.
2. Thiết bị mạng: modem Viettel FTTH, Media Converter D-Link, Router TP-Link và card mạng.
3. HDD: bảng cấu tạo ổ cứng tháo rời.
4. RAM/CPU: bảng phân biệt RAM DDR1–DDR5 và các socket CPU.
5. Bàn phím/chuột: lưu làm tài liệu tham khảo mở rộng, chưa tạo mã QR riêng vì bộ QR lõi hiện vẫn gồm 9 thiết bị.

Hai video do giáo viên cung cấp được đặt trong mục **Video tổng quan tham khảo** cho nhóm phần cứng. Không gắn nhầm chúng thành video chuyên biệt của một linh kiện. Nội dung và âm thanh nguồn được giữ nguyên; không tự nhận đã làm sạch hoặc cải thiện giọng đọc. Giáo viên cần xác nhận quyền sử dụng trước khi chia sẻ rộng rãi.

## QR: quy trình chuẩn
1. Chạy `START_SMART_STEM.bat`; máy chủ được bind `0.0.0.0:8000` để thiết bị khác trong LAN truy cập.
2. Mở dashboard trên máy giáo viên.
3. Kiểm tra IP LAN tự dò trong ô địa chỉ QR. Nếu máy có nhiều card mạng/VPN, đối chiếu bằng `ipconfig` và sửa thành IP của Wi-Fi/LAN đang dùng, ví dụ `http://192.168.1.20:8000`.
4. Nhấn **Tạo QR toàn bộ thiết bị**.
5. Mở `/api/qr/export.zip` sau khi tạo mã.
6. Dùng điện thoại cùng mạng Wi-Fi quét thử; QR phải mở trang `/d/<mã-thiết-bị>`.

## Nếu QR vẫn không mở
- Cho phép Python/uvicorn qua Windows Defender Firewall trên mạng Private.
- Tắt tạm VPN trên máy tính khi xác định IP.
- Không dùng Wi-Fi Guest hoặc AP/client isolation.
- Kiểm tra máy tính và điện thoại cùng mạng con.
- Đảm bảo cổng TCP 8000 không bị phần mềm khác chiếm.
- Mạng trường học có thể chặn thiết bị Wi-Fi truy cập máy tính; cần quản trị mạng mở luồng nội bộ.

## Hạn chế đã công khai
- QR LAN chỉ hoạt động trong cùng mạng hoặc khi có định tuyến phù hợp. Muốn truy cập ngoài trường cần hosting/domain/HTTPS và bảo mật bổ sung.
- 9 mô hình GLB hiện có là mô hình minh họa, không phải bản quét/CAD chính xác của thiết bị thật. Không quảng bá là mô hình AR khớp 100%.
- 9 video MP4 ban đầu vẫn là video minh họa đã có; chưa được thay thế bằng 9 video quay/chụp thực tế có lời thuyết minh thu âm chuyên nghiệp. Hai video mới do giáo viên gửi chỉ là tài liệu tổng quan tham khảo.
- Trang học tập ghi nhận lượt quét, phát video và câu trả lời ẩn danh; không xác định danh tính học sinh.
- Bảo toàn cơ sở dữ liệu cũ: sao lưu `data/smart_stem.db` trước khi cập nhật.

## Cấu trúc tư liệu
- `storage/reference_images/`: 5 ảnh tư liệu do giáo viên cung cấp.
- `storage/reference_videos/`: 2 video tổng quan do giáo viên cung cấp.
- `storage/videos/`: 9 video minh họa thiết bị hiện có.
- `storage/models3d/`: 9 mô hình GLB minh họa hiện có.
