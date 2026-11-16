# SMART STEM – Tải mô hình 3D từ máy tính (V2.5)

## Cách sử dụng
1. Mở trang quản trị SMART STEM.
2. Chọn Thêm thiết bị hoặc Sửa thiết bị.
3. Tại mục “Tải mô hình 3D từ máy tính”, chọn tệp `.glb` hoặc `.gltf`.
4. Nhấn Lưu thiết bị. Phần mềm tải tệp lên máy chủ và tự điền đường dẫn mô hình.
5. Mở thiết bị trong danh sách để xem trước mô hình 3D; trang QR của thiết bị cũng sử dụng đường dẫn này.

## Định dạng
- Khuyến nghị `.glb` vì thường đóng gói hình học, vật liệu và texture trong một tệp.
- `.gltf` được chấp nhận, nhưng nếu tham chiếu tệp `.bin` hoặc ảnh bên ngoài thì phải đưa các tài nguyên đó lên đúng cấu trúc đường dẫn; tải riêng `.gltf` có thể làm mô hình thiếu dữ liệu.
- Giới hạn tải lên: 200 MB/tệp.

## Lưu trữ và sao lưu
Tệp tải lên được lưu tại `storage/models3d/uploaded/`. Khi triển khai Docker, phải mount thư mục `storage` thành volume bền vững và đưa thư mục này vào bản sao lưu. Không xóa thư mục này khi nâng cấp phần mềm.
