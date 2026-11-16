# QUẢN LÝ VIDEO – SMART STEM 2.3

Trong hộp thoại Thêm/Sửa thiết bị có hai cách gắn video:

## A. Chọn video từ máy tính giáo viên
1. Bấm `Thêm thiết bị` hoặc `Sửa`.
2. Tại mục `Video từ máy tính`, bấm `Choose file/Chọn tệp`.
3. Chọn MP4, WebM, OGG, MOV hoặc M4V (tối đa 500 MB).
4. Bấm `Lưu thiết bị`. Video được tải lên thư mục `storage/uploaded_videos` của máy chủ và tự gắn với thiết bị.
5. Không cần tải video vào từng điện thoại học sinh. Học sinh quét QR để xem video từ máy chủ.

## B. Dán liên kết video bên ngoài
- YouTube: dán URL video hoặc dạng youtu.be. Trang QR sẽ nhúng trình phát YouTube.
- Vimeo: dán URL video Vimeo. Trang QR sẽ nhúng trình phát Vimeo.
- Link MP4/WebM/OGG/MOV/M4V trực tiếp: dán URL kết thúc bằng phần mở rộng video; trình duyệt phát bằng trình phát video.
- Link trang web khác: hệ thống hiện liên kết `Mở video/trang nguồn`. Không phải website nào cũng cho phép nhúng hoặc phát trực tiếp.

## Lưu ý
- Máy chủ cần có Internet để tải video từ nguồn ngoài.
- YouTube/Vimeo có thể không cho nhúng nếu chủ video tắt quyền nhúng, giới hạn khu vực/độ tuổi hoặc trình duyệt chặn cookie.
- Link ngoài có thể bị chủ nguồn xóa/thay đổi; hệ thống không lưu bản sao.
- Với video chọn từ máy tính, dung lượng tối đa 500 MB mỗi tệp; nên ưu tiên MP4 H.264/AAC, 720p hoặc 1080p, âm thanh rõ.
- Video tải lên nằm trong `storage/uploaded_videos`. Sao lưu thư mục này cùng `data/smart_stem.db`.
- Khi sửa thiết bị, nếu chọn tệp mới thì tệp mới sẽ thay nguồn video hiện tại. Nếu không chọn tệp mới, đường dẫn ở ô liên kết được giữ và lưu.
