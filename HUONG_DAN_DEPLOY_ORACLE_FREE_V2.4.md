# SMART STEM V2.4 – triển khai Internet bằng Oracle Cloud Always Free

## Lưu ý quan trọng
- Gói này là bộ triển khai Docker cho VPS Ubuntu, không phải tài khoản máy chủ đã được tạo sẵn.
- Oracle Always Free có thể dùng 0 đồng nếu chỉ tạo tài nguyên đúng nhãn Always Free và trong hạn mức. Oracle không cấp SLA cho tài khoản miễn phí; máy ảo nhàn rỗi có thể bị thu hồi. Vì vậy không thể cam kết uptime tuyệt đối 24/24.
- Oracle có thể yêu cầu số điện thoại và thẻ để xác minh. Đọc kỹ màn hình tạo tài nguyên, không tạo tài nguyên trả phí.
- Trước khi chuyển dữ liệu thật, sao lưu toàn bộ thư mục `data/` và `storage/` của máy đang chạy. Không dùng bản mới để ghi đè dữ liệu gốc.

## Phần đã chuẩn bị trong gói
- Dockerfile và docker-compose với volume bền vững `./data` và `./storage`.
- `restart: unless-stopped`, healthcheck và Caddy cấp HTTPS tự động.
- `PUBLIC_BASE_URL` để QR dùng URL Internet.
- Đã bỏ lệnh xóa NW-MC-01/NW-MC-02 và lịch sử sự kiện khi khởi động; các bản ghi cũ được giữ nguyên.
- SQLite và storage vẫn dùng đúng cấu trúc ứng dụng hiện tại.

## A. Tạo máy chủ miễn phí
1. Mở https://www.oracle.com/cloud/free/ và đăng ký Oracle Cloud Free Tier.
2. Chọn Home Region phù hợp gần Việt Nam nếu có; Home Region không đổi dễ dàng.
3. Tạo Compute VM Ubuntu, chọn shape có nhãn **Always Free Eligible** (ưu tiên Ampere A1 trong hạn mức hiện hành). Không chọn shape trả phí.
4. Cấu hình public IPv4, SSH key; mở TCP 22 (chỉ IP quản trị nếu có thể), 80 và 443 trong Security List/Network Security Group và firewall Ubuntu.
5. Ghi lại public IPv4. Nếu A1 báo out of host capacity, chờ hoặc thử availability domain khác; không chuyển sang tài nguyên tính phí.

## B. Tên miền miễn phí
1. Tạo hostname miễn phí tại https://www.duckdns.org/ và lấy token.
2. Trỏ hostname về public IPv4 của VM bằng trang DuckDNS.
3. Chờ DNS cập nhật. Không chia sẻ token DuckDNS.

## C. Cài Docker trên Ubuntu
Chạy lần lượt qua SSH:

```bash
sudo apt update
sudo apt install -y ca-certificates curl git ufw
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
. /etc/os-release
 echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"
```
Đăng xuất SSH rồi đăng nhập lại. Mở firewall:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## D. Chuyển dữ liệu V2.4
1. Trên máy Windows, giữ nguyên thư mục bản V2.4 đang chạy.
2. Sao lưu nguyên thư mục `data` và `storage`; nén thành hai tệp riêng.
3. Tải gói này lên VM và giải nén. Chuyển thư mục `data` và `storage` đã sao lưu vào thư mục dự án, không thay bằng thư mục rỗng trong ZIP.
4. Tạo cấu hình:

```bash
cp .env.example .env
nano .env
```
Điền `SITE_DOMAIN`, `PUBLIC_BASE_URL` (phải là https://tên-miền) và `ACME_EMAIL`.
5. Đảm bảo thư mục `data` có `smart_stem.db` nếu đã có dữ liệu; không khởi động lần đầu với DB trống nếu muốn chuyển nguyên dữ liệu.
6. Chạy:

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f --tail=100
```

## E. Kiểm tra và tạo QR
- Mở `https://TEN-MIEN/api/health`, cần trả JSON status ok.
- Mở trang chủ và kiểm tra các thiết bị, hình ảnh, video, câu hỏi.
- Tạo lại QR bằng URL công khai:

```bash
curl -X POST 'https://TEN-MIEN/api/qr/generate-all?request_base=https%3A%2F%2FTEN-MIEN'
```
- Quét QR bằng điện thoại dùng 4G/5G, không chỉ thử trên Wi-Fi nội bộ.

## F. Sao lưu tự động
Thiết lập cron hằng ngày lúc 02:00:

```bash
crontab -e
```
Thêm dòng (sửa đường dẫn đúng):

```cron
0 2 * * * cd /opt/SMART_COMPUTER_NETWORK_STEM_V1.0 && bash deploy/backup.sh >> backups/backup.log 2>&1
```
Sao lưu tại cùng máy chủ chưa đủ an toàn. Định kỳ tải bản backup ra máy tính/ổ cứng hoặc kho lưu trữ độc lập.

## G. Bảo mật trước khi công khai
Bản V2.4 gốc cần được rà soát bổ sung xác thực/phân quyền quản trị cho các API thay đổi dữ liệu và upload. Không công khai URL quản trị cho học sinh trước khi khóa các API quản trị. CORS `*` cũng cần giới hạn theo tên miền. Không đặt token, mật khẩu hoặc khóa SSH trong ZIP hay gửi qua chat.

## Khôi phục
Dùng hướng dẫn trong `deploy/restore-warning.txt`. Luôn sao lưu trạng thái hiện tại trước khi phục hồi.


## Bổ sung V2.5 – lưu mô hình 3D tải lên
Thư mục `storage` phải được mount thành volume bền vững. Mô hình 3D tải lên được lưu tại `storage/models3d/uploaded/`; hãy đưa toàn bộ `storage` vào quy trình sao lưu và không xóa khi cập nhật container.
