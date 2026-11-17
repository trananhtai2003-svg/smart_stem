from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, joinedload
from pathlib import Path
from urllib.parse import quote
import qrcode, json, asyncio, csv, io, zipfile, socket, ipaddress, uuid, re, os
from .database import Base, engine, get_db, SessionLocal
from . import models, schemas

ROOT = Path(__file__).resolve().parents[2]
STORAGE = ROOT / "storage"
QR_DIR = STORAGE / "qr"
UPLOAD_VIDEO_DIR = STORAGE / "uploaded_videos"
UPLOAD_MODEL_DIR = STORAGE / "models3d" / "uploaded"
for p in [STORAGE/"images", STORAGE/"videos", STORAGE/"models3d", QR_DIR, UPLOAD_VIDEO_DIR, UPLOAD_MODEL_DIR]:
    p.mkdir(parents=True, exist_ok=True)

Base.metadata.create_all(bind=engine)
app = FastAPI(title="SMART STEM QR Learning", version="2.5.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/storage", StaticFiles(directory=STORAGE), name="storage")
UI_DIR = ROOT / "frontend_single"


MODULES = [
 ("HW","Phần cứng máy tính","Mainboard, CPU, RAM và thiết bị lưu trữ"),
 ("NW","Thiết bị mạng","Modem, Router và Card mạng"),
]
SEED = [
 ("NW-MODEM-01","Modem Viettel FTTH","NW","Thiết bị kết nối mạng truy nhập Internet","Kết nối mạng truy nhập"),
 ("NW-ROUTER-01","Router TP-Link","NW","Thiết bị kết nối và phân phối mạng","Định tuyến và phân phối kết nối"),
 ("NW-NIC-01","Card mạng","NW","Bộ điều hợp giao tiếp mạng","Kết nối máy tính với mạng"),
 ("HW-MAIN-01","Mainboard","HW","Bo mạch chủ kết nối các thành phần máy tính","Kết nối CPU, RAM và thiết bị"),
 ("HW-HDD-01","Ổ cứng HDD","HW","Thiết bị lưu trữ dữ liệu từ tính","Lưu trữ dữ liệu lâu dài"),
 ("HW-RAM-01","Bộ nhớ RAM","HW","Bộ nhớ truy cập ngẫu nhiên","Lưu trữ tạm dữ liệu đang sử dụng"),
 ("HW-CPU-01","CPU","HW","Bộ xử lý trung tâm","Thực hiện lệnh và xử lý dữ liệu"),
 ("HW-KB-01","Bàn phím máy tính","HW","Thiết bị nhập liệu dùng để đưa ký tự, số và lệnh vào máy tính","Nhập văn bản, số liệu và lệnh điều khiển"),
 ("HW-MOUSE-01","Chuột máy tính","HW","Thiết bị trỏ giúp điều khiển con trỏ và thao tác trên giao diện máy tính","Di chuyển con trỏ, nhấp, chọn, kéo thả và cuộn")
]
def seed():
    db=SessionLocal()
    try:
        if db.query(models.Module).count()==0:
            for c,n,d in MODULES: db.add(models.Module(code=c,name=n,description=d))
            db.commit()
        lookup={m.code:m.id for m in db.query(models.Module).all()}
        if "NW" in lookup:
            db.query(models.Module).filter_by(code="NW").update({"description":"Modem, Router và Card mạng"}, synchronize_session=False)
        # Preserve legacy device records and event history during upgrades/deployments.
        for code,name,mod,desc,func in SEED:
            if not db.query(models.Device).filter_by(code=code).first():
                db.add(models.Device(code=code,name=name,module_id=lookup[mod],description=desc,function=func))
        VIDEO_DEFAULTS = {
        "HW-CPU-01": "/storage/videos/cpu.mp4", "HW-RAM-01": "/storage/videos/ram.mp4",
        "HW-MAIN-01": "/storage/videos/mainboard.mp4", "HW-HDD-01": "/storage/videos/hdd.mp4",
        "NW-MODEM-01": "/storage/videos/modem.mp4", "NW-ROUTER-01": "/storage/videos/router.mp4",
        "NW-NIC-01": "/storage/videos/network_card.mp4"
    }
        for code, path in VIDEO_DEFAULTS.items():
            obj = db.query(models.Device).filter_by(code=code).first()
            if obj and (not obj.video_path or not (ROOT / "storage" / "videos" / Path(path).name).exists()):
                if obj and (ROOT / "storage" / "videos" / Path(path).name).exists(): obj.video_path = path
        MODEL_DEFAULTS = {
            "HW-CPU-01": "/storage/models3d/cpu.glb",
            "HW-RAM-01": "/storage/models3d/ram.glb",
            "HW-MAIN-01": "/storage/models3d/mainboard.glb",
            "HW-HDD-01": "/storage/models3d/hdd.glb",
            "NW-MODEM-01": "/storage/models3d/modem.glb",
            "NW-ROUTER-01": "/storage/models3d/router.glb",
            "NW-NIC-01": "/storage/models3d/network_card.glb"
        }
        for code, path in MODEL_DEFAULTS.items():
            obj = db.query(models.Device).filter_by(code=code).first()
            if obj and (not obj.model3d_path or not (ROOT / "storage" / "models3d" / Path(path).name).exists()):
                if obj and (ROOT / "storage" / "models3d" / Path(path).name).exists(): obj.model3d_path = path
        db.commit()
    finally: db.close()
seed()

class Hub:
    def __init__(self): self.clients=set()
    async def connect(self, ws):
        await ws.accept(); self.clients.add(ws)
    def disconnect(self, ws): self.clients.discard(ws)
    async def broadcast(self, data):
        dead=[]
        for ws in list(self.clients):
            try: await ws.send_json(data)
            except: dead.append(ws)
        for ws in dead: self.disconnect(ws)
hub=Hub()

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(UI_DIR / "index.html")

@app.get("/api/health")
def health(): return {"status":"ok","version":"2.5.0","modules":2,"seed_devices":9,"mode":"QR_LEARNING"}

@app.get("/api/modules", response_model=list[schemas.ModuleOut])
def modules(db:Session=Depends(get_db)): return db.query(models.Module).filter(models.Module.code.in_(["HW", "NW"])).order_by(models.Module.id).all()

@app.get("/api/devices", response_model=list[schemas.DeviceOut])
def devices(db:Session=Depends(get_db)): return db.query(models.Device).order_by(models.Device.code).all()

@app.post("/api/models3d/upload")
async def upload_model3d(file: UploadFile = File(...)):
    """Upload a 3D model. GLB is self-contained and recommended; GLTF may need sidecar files."""
    allowed = {".glb", ".gltf"}
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(400, "Chỉ hỗ trợ mô hình .glb hoặc .gltf. Khuyến nghị dùng .glb.")
    max_bytes = 200 * 1024 * 1024
    safe_name = f"{uuid.uuid4().hex}{suffix}"
    target = UPLOAD_MODEL_DIR / safe_name
    total = 0
    try:
        with target.open("wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    out.close()
                    target.unlink(missing_ok=True)
                    raise HTTPException(413, "Mô hình 3D vượt quá giới hạn 200 MB.")
                out.write(chunk)
    finally:
        await file.close()
    if total == 0:
        target.unlink(missing_ok=True)
        raise HTTPException(400, "Tệp mô hình 3D rỗng.")
    return {"model3d_path": f"/storage/models3d/uploaded/{safe_name}", "filename": file.filename, "size": total}


@app.post("/api/videos/upload")
async def upload_video(file: UploadFile = File(...)):
    allowed = {".mp4", ".webm", ".ogg", ".mov", ".m4v"}
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(400, "Định dạng chưa hỗ trợ. Hãy chọn MP4, WebM, OGG, MOV hoặc M4V.")
    max_bytes = 500 * 1024 * 1024
    safe_name = f"{uuid.uuid4().hex}{suffix}"
    target = UPLOAD_VIDEO_DIR / safe_name
    total = 0
    try:
        with target.open("wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk: break
                total += len(chunk)
                if total > max_bytes:
                    out.close()
                    target.unlink(missing_ok=True)
                    raise HTTPException(413, "Video vượt quá giới hạn 500 MB.")
                out.write(chunk)
    finally:
        await file.close()
    if total == 0:
        target.unlink(missing_ok=True)
        raise HTTPException(400, "Tệp video rỗng.")
    return {"video_path": f"/storage/uploaded_videos/{safe_name}", "filename": file.filename, "size": total}

def validate_video_source(value):
    value = (value or "").strip()
    if not value: return
    if value.startswith("/storage/videos/") or value.startswith("/storage/uploaded_videos/"):
        return
    if value.startswith("https://") or value.startswith("http://"):
        return
    raise HTTPException(400, "Nguồn video phải là video đã tải lên hoặc URL bắt đầu bằng http:// hay https://.")

@app.post("/api/devices", response_model=schemas.DeviceOut)
def create_device(data:schemas.DeviceCreate, db:Session=Depends(get_db)):
    validate_video_source(data.video_path)
    if db.query(models.Device).filter_by(code=data.code).first(): raise HTTPException(409,"Mã thiết bị đã tồn tại")
    if not db.query(models.Module).filter_by(id=data.module_id).first(): raise HTTPException(404,"Không tìm thấy mô-đun")
    obj=models.Device(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj); return obj

@app.get("/api/devices/{code}", response_model=schemas.DeviceOut)
def get_device(code:str, db:Session=Depends(get_db)):
    obj=db.query(models.Device).filter_by(code=code).first()
    if not obj: raise HTTPException(404,"Không tìm thấy thiết bị")
    return obj

@app.put("/api/devices/{code}", response_model=schemas.DeviceOut)
def update_device(code:str, data:schemas.DeviceCreate, db:Session=Depends(get_db)):
    validate_video_source(data.video_path)
    obj=db.query(models.Device).filter_by(code=code).first()
    if not obj: raise HTTPException(404,"Không tìm thấy thiết bị")
    for k,v in data.model_dump().items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj); return obj

@app.delete("/api/devices/{code}")
def delete_device(code:str, db:Session=Depends(get_db)):
    obj=db.query(models.Device).filter_by(code=code).first()
    if not obj: raise HTTPException(404,"Không tìm thấy thiết bị")
    db.delete(obj); db.commit(); return {"deleted":code}

def get_lan_ip():
    """Best-effort LAN IPv4 address used by phones on the same network."""
    candidates = []
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("192.0.2.1", 80))
            candidates.append(sock.getsockname()[0])
    except Exception:
        pass
    try:
        candidates.extend(socket.gethostbyname_ex(socket.gethostname())[2])
    except Exception:
        pass
    for ip in candidates:
        try:
            addr = ipaddress.ip_address(ip)
            if addr.version == 4 and not addr.is_loopback and not addr.is_link_local:
                return ip
        except ValueError:
            continue
    return "127.0.0.1"

@app.get("/api/network-info")
def network_info():
    public_url = os.getenv("PUBLIC_BASE_URL", "https://smart-stem.onrender.com")
    if public_url:
        return {"lan_ip": "cloud", "suggested_base": public_url.rstrip("/"),
                "warning": "Máy chủ đang chạy trực tuyến trên đám mây."}
    ip = get_lan_ip()
    return {"lan_ip": ip, "suggested_base": f"http://{ip}:8000",
            "warning": "Điện thoại phải cùng Wi-Fi/LAN với máy chủ; cho phép Python/FastAPI qua Windows Firewall."}

def make_qr(code:str, request_base:str):
    url=f"{request_base.rstrip('/')}/d/{quote(code)}"
    path=QR_DIR/f"{code}.png"
    qrcode.make(url).save(path)
    return f"/storage/qr/{path.name}",url

@app.post("/api/qr/generate-all")
def generate_all(request_base:str="", db:Session=Depends(get_db)):
    request_base = (request_base or os.getenv("PUBLIC_BASE_URL") or f"http://{get_lan_ip()}:8000").rstrip("/")
    if any(x in request_base.lower() for x in ["localhost", "127.0.0.1", "0.0.0.0"]):
        raise HTTPException(400, "QR không được dùng localhost/127.0.0.1. Hãy dùng IP LAN của máy tính giáo viên.")
    result=[]
    for obj in db.query(models.Device).all():
        path,url=make_qr(obj.code,request_base); obj.qr_path=path
        result.append({"device_code":obj.code,"qr_path":path,"url":url})
    db.commit(); return result

@app.post("/api/qr/{code}")
def generate_qr(code:str, request_base:str="", db:Session=Depends(get_db)):
    obj=db.query(models.Device).filter_by(code=code).first()
    if not obj: raise HTTPException(404,"Không tìm thấy thiết bị")
    request_base = (request_base or os.getenv("PUBLIC_BASE_URL") or f"http://{get_lan_ip()}:8000").rstrip("/")
    if any(x in request_base.lower() for x in ["localhost", "127.0.0.1", "0.0.0.0"]):
        raise HTTPException(400, "QR không được dùng localhost/127.0.0.1. Hãy dùng IP LAN của máy tính giáo viên.")
    path,url=make_qr(code,request_base); obj.qr_path=path; db.commit()
    return {"device_code":code,"qr_path":path,"url":url}

@app.get("/api/qr/export.zip")
def export_qr_zip(db:Session=Depends(get_db)):
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as zf:
        for obj in db.query(models.Device).filter_by(active=True).order_by(models.Device.code).all():
            path=QR_DIR/f"{obj.code}.png"
            if path.exists(): zf.write(path,arcname=f"QR_{obj.code}.png")
    buf.seek(0)
    return StreamingResponse(buf,media_type="application/zip",headers={"Content-Disposition":"attachment; filename=SMART_STEM_QR_CODES.zip"})

@app.get("/d/{code}", response_class=HTMLResponse)
def public_device(code:str, db:Session=Depends(get_db)):
    obj=db.query(models.Device).filter_by(code=code,active=True).first()
    if not obj: raise HTTPException(404,"Thiết bị không tồn tại")
    db.add(models.DeviceEvent(device_code=code,event_type="QR_SCAN",source="qr",payload="{}")); db.commit()
    import html
    name=html.escape(obj.name); desc=html.escape(obj.description or ""); func=html.escape(obj.function or "")
    reference_map = {
      "HW-MAIN-01": ("mainboard_reference.png", "Sơ đồ chú thích Mainboard"),
      "HW-HDD-01": ("hdd_reference.png", "Sơ đồ cấu tạo HDD tháo rời"),
      "HW-RAM-01": ("ram_cpu_reference.png", "Bảng phân biệt RAM DDR1–DDR5"),
      "HW-CPU-01": ("ram_cpu_reference.png", "Bảng tham chiếu CPU và các loại socket"),
      "NW-MODEM-01": ("network_devices_reference.png", "Sơ đồ thiết bị mạng"),
      "NW-ROUTER-01": ("network_devices_reference.png", "Sơ đồ thiết bị mạng"),
      "HW-KB-01": ("keyboard_mouse_reference.png", "Bàn phím máy tính và các nhóm phím"),
      "HW-MOUSE-01": ("keyboard_mouse_reference.png", "Chuột máy tính và các thao tác cơ bản"),
      "NW-NIC-01": ("network_devices_reference.png", "Sơ đồ thiết bị mạng")
    }
    ref = reference_map.get(code)
    reference_html = (f"<section class='section'><h2>📚 Tài liệu hình ảnh tham khảo</h2><p class='muted'>Tư liệu do giáo viên cung cấp, dùng để quan sát và đối chiếu cấu tạo.</p><img class='ref-image' src='/storage/reference_images/{ref[0]}' alt='{html.escape(ref[1])}'><p class='muted'>{html.escape(ref[1])}</p></section>" if ref else "")
    reference_videos = ""
    if code in ("HW-CPU-01","HW-RAM-01","HW-MAIN-01","HW-HDD-01"):
           reference_videos = "<section class='section'><h2>🎞 Video tổng quan tham khảo</h2><p class='muted'>Hai video này là tư liệu tổng quan, không phải video chuyên biệt cho riêng linh kiện đang xem.</p><h3>Cấu trúc máy tính</h3><div class='video-frame'><iframe src='https://www.youtube-nocookie.com/embed/GZpw0POlIwY' title='Cấu trúc máy tính tham khảo' allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share' allowfullscreen></iframe></div><h3 style='margin-top:14px'>Hiểu các bộ phận trong máy tính</h3><div class='video-frame'><iframe src='https://www.youtube-nocookie.com/embed/I1oIsQdwWzM' title='Hiểu các bộ phận trong máy tính tham khảo' allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share' allowfullscreen></iframe></div></section>"
    video_path = (obj.video_path or "").strip()
    yt = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([A-Za-z0-9_-]{6,})", video_path)
    vimeo = re.search(r"vimeo\.com/(?:video/)?([0-9]+)", video_path)
    if yt:
        video = f'<div class="video-frame"><iframe src="https://www.youtube-nocookie.com/embed/{yt.group(1)}" title="Video học tập" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>'
    elif vimeo:
        video = f'<div class="video-frame"><iframe src="https://player.vimeo.com/video/{vimeo.group(1)}" title="Video học tập" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe></div>'
    elif video_path.startswith(("http://","https://")):
        if re.search(r"\.(mp4|webm|ogg|mov|m4v)(?:[?#].*)?$", video_path, re.I):
            video = f'<video id="learningVideo" controls playsinline preload="metadata" src="{html.escape(video_path, quote=True)}"></video>'
        else:
            video = f'<p class="muted">Nguồn video bên ngoài: <a href="{html.escape(video_path, quote=True)}" target="_blank" rel="noopener">Mở video trong trang nguồn</a>. Nếu nguồn không cho nhúng, học sinh có thể mở liên kết này.</p>'
    elif video_path:
        video = f'<video id="learningVideo" controls playsinline preload="metadata" src="{html.escape(video_path, quote=True)}"></video>'
    else:
        video = '<p class="empty">Chưa cập nhật video. Giáo viên có thể tải video từ máy tính hoặc dán liên kết video bên ngoài.</p>' 
    model=(f'<model-viewer src="{html.escape(obj.model3d_path)}" camera-controls auto-rotate ar ar-modes="webxr scene-viewer quick-look" shadow-intensity="1" alt="Mô hình 3D minh họa {name}"></model-viewer>' if obj.model3d_path else '<p class="empty">Chưa cập nhật mô hình 3D cho thiết bị này.</p>')
    quiz_bank = {
      "HW-CPU-01":("CPU thực hiện chu trình xử lý lệnh theo trình tự nào?",["Nhận lệnh – Giải mã – Thực thi","Lưu trữ – In – Quét","Khởi động – Tắt – Xóa"],0,"CPU lấy lệnh, giải mã rồi thực thi."),
      "HW-RAM-01":("Điều gì xảy ra với dữ liệu trong RAM khi mất điện?",["Được lưu vĩnh viễn","Bị mất","Tự chuyển vào CPU"],1,"RAM là bộ nhớ khả biến."),
      "HW-MAIN-01":("Vai trò chính của mainboard là gì?",["Kết nối và phối hợp linh kiện","Chỉ lưu tệp","Chỉ hiển thị hình ảnh"],0,"Mainboard tạo nền tảng kết nối."),
      "HW-HDD-01":("Bộ phận nào đọc/ghi dữ liệu trên HDD?",["Đầu từ đọc/ghi","Quạt tản nhiệt","Cổng USB"],0,"Đầu từ truy xuất dữ liệu trên đĩa từ."),
      "NW-MODEM-01":("Modem chủ yếu đảm nhiệm chức năng gì?",["Giao tiếp/chuyển đổi tín hiệu đường truyền","Định tuyến giữa mọi mạng LAN","Lưu trữ dữ liệu"],0,"Modem giao tiếp với môi trường truyền dẫn."),
      "NW-ROUTER-01":("Router dựa vào thông tin nào để chọn đường đi?",["Địa chỉ IP đích và bảng định tuyến","Tên tệp Word","Dung lượng RAM"],0,"Router tra bảng định tuyến để chuyển tiếp gói tin."),
      "HW-KB-01":("Bàn phím máy tính dùng chủ yếu để làm gì?",["Nhập ký tự, số và lệnh vào máy tính","Hiển thị hình ảnh","Lưu trữ dữ liệu"],0,"Bàn phím là thiết bị nhập liệu."),
      "HW-MOUSE-01":("Thao tác nào thường được thực hiện bằng chuột máy tính?",["Di chuyển con trỏ, nhấp và kéo thả","In tài liệu","Lưu điện năng"],0,"Chuột là thiết bị trỏ dùng để điều khiển con trỏ và thao tác trên giao diện."),
      "NW-NIC-01":("NIC có vai trò gì?",["Cung cấp giao tiếp mạng cho máy tính","Điều khiển màn hình","Lưu hệ điều hành"],0,"NIC gửi và nhận khung dữ liệu qua mạng.")
    }
    q=quiz_bank.get(code)
    quiz_html=""
    if q:
        qtext=html.escape(q[0]); opts="".join(f"<button class='answer' onclick='checkAnswer({i},this)'>{chr(65+i)}. {html.escape(a)}</button>" for i,a in enumerate(q[1]))
        quiz_html=f"<section class='section' id='quiz'><h2>🧠 Kiểm tra nhanh</h2><p><b>{qtext}</b></p><div class='answers'>{opts}</div><p id='feedback' aria-live='polite'></p></section>"
        quiz_script=f"<script>let answered=false;async function checkAnswer(i,btn){{if(answered)return;answered=true;const ok=i==={q[2]};document.querySelectorAll('.answer').forEach((b,n)=>{{b.disabled=true;if(n==={q[2]})b.classList.add('correct')}});if(!ok)btn.classList.add('wrong');document.getElementById('feedback').textContent=(ok?'Chính xác! ':'Chưa đúng. ')+{json.dumps(q[3],ensure_ascii=False)};try{{await fetch('/api/events',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{device_code:{json.dumps(code)},event:'QUIZ_ANSWER',source:'qr_student',answer:i,correct:ok}})}})}}catch(e){{}}}}</script>"
    else: quiz_script=""
    page=f"""<!doctype html><html lang='vi'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><meta name='theme-color' content='#12366a'><title>{name} - SMART STEM</title><script type='module' src='https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js'></script><style>
    *{{box-sizing:border-box}}body{{font:16px/1.6 system-ui,Arial;margin:0;background:#f2f6fc;color:#17243a}}header{{background:#12366a;color:white;padding:20px max(16px,calc((100% - 900px)/2))}}header small{{color:#c9d8f4}}main{{max-width:900px;margin:20px auto;padding:0 14px}}.hero,.section{{background:white;border:1px solid #e0e8f3;border-radius:16px;padding:18px;margin-bottom:14px;box-shadow:0 4px 18px #18365f0b}}h1{{font-size:23px;margin:0 0 4px}}h2{{font-size:19px;margin:0 0 12px}}.code{{display:inline-block;background:#eaf1ff;color:#174a9a;border-radius:30px;padding:3px 10px;font-size:13px}}.muted,.empty{{color:#64748b}}video{{width:100%;max-height:420px;background:#101827;border-radius:12px}}.video-frame{{position:relative;width:100%;aspect-ratio:16/9;background:#101827;border-radius:12px;overflow:hidden}}.video-frame iframe{{width:100%;height:100%;border:0}}.ref-image{{display:block;width:100%;height:auto;border:1px solid #dbe5f2;border-radius:12px}}model-viewer{{width:100%;height:320px;background:#f1f5f9;border-radius:12px}}.answer{{display:block;width:100%;text-align:left;border:1px solid #dbe5f2;border-radius:10px;padding:13px;margin:8px 0;background:#fff;font:inherit;cursor:pointer}}.answer:disabled{{cursor:default;opacity:1}}.answer.correct{{background:#dcfce7;border-color:#16a34a}}.answer.wrong{{background:#fee2e2;border-color:#dc2626}}#feedback{{font-weight:600}}footer{{text-align:center;color:#64748b;font-size:13px;padding:20px}}@media(max-width:600px){{main{{margin:12px auto}}.hero,.section{{padding:15px}}model-viewer{{height:270px}}}}
    </style></head><body><header><h1>SMART COMPUTER & NETWORK STEM</h1><small>Không cần đăng nhập · Quét mã để tự học</small></header><main><section class='hero'><h1>{name}</h1><span class='code'>{html.escape(code)}</span><p>{desc}</p><p><b>Chức năng:</b> {func}</p></section><section class='section'><h2>🔎 Khám phá mô hình 3D / AR</h2>{model}<p class='muted'>Xoay mô hình bằng thao tác chạm/kéo. AR phụ thuộc thiết bị và trình duyệt hỗ trợ.</p></section><section class='section'><h2>🎬 Video tìm hiểu</h2>{video}</section>{reference_html}{reference_videos}{quiz_html}<footer>SMART STEM · Học tập tự do qua QR Code · Không thu thập họ tên, mã lớp hoặc mã học sinh</footer></main><script>const v=document.getElementById('learningVideo');if(v)v.addEventListener('play',()=>fetch('/api/events',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{device_code:{json.dumps(code)},event:'VIDEO_PLAY',source:'qr_student'}})}}).catch(()=>{{}}));</script>{quiz_script}</body></html>"""
    return HTMLResponse(page)

@app.post("/api/events")
async def create_event(data:dict, db:Session=Depends(get_db)):
    code=data.get("target") or data.get("device_code")
    if not code: raise HTTPException(400,"Thiếu mã thiết bị")
    if not db.query(models.Device).filter_by(code=code).first():
        raise HTTPException(404,"Mã thiết bị không tồn tại")
    event_type=data.get("event","BUTTON_PRESS")
    allowed_events={"QR_SCAN","VIDEO_PLAY","QUIZ_ANSWER","DEVICE_OPEN","BUTTON_PRESS","DEVICE_SELECT"}
    if event_type not in allowed_events: raise HTTPException(400,"Loại sự kiện không hợp lệ")
    db.add(models.DeviceEvent(device_code=code,event_type=event_type,source=data.get("source","web"),payload=json.dumps(data,ensure_ascii=False)))
    db.commit()
    if event_type in ("BUTTON_PRESS","DEVICE_SELECT"):
        await hub.broadcast({"type":"device_event","device_code":code,"event":event_type})
    return {"accepted":True,"device_code":code,"event":event_type}

@app.get("/api/events/recent")
def recent_events(db:Session=Depends(get_db)):
    rows=db.query(models.DeviceEvent).order_by(models.DeviceEvent.id.desc()).limit(50).all()
    return [{"id":x.id,"device_code":x.device_code,"event_type":x.event_type,"source":x.source,"created_at":x.created_at.isoformat()} for x in rows]


@app.get("/api/analytics/summary")
def analytics_summary(db:Session=Depends(get_db)):
    from datetime import datetime, timezone
    today=datetime.now(timezone.utc).date()
    events=db.query(models.DeviceEvent).all()
    today_events=[e for e in events if e.created_at and e.created_at.date()==today]
    scans=[e for e in events if e.event_type=="QR_SCAN"]
    quizzes=[e for e in events if e.event_type=="QUIZ_ANSWER"]
    correct=0
    for e in quizzes:
        try:
            if json.loads(e.payload or "{}").get("correct"): correct+=1
        except Exception: pass
    return {"devices":db.query(models.Device).count(),"modules":db.query(models.Module).filter(models.Module.code.in_(["HW", "NW"])).count(),
            "events_total":len(events),"events_today":len(today_events),"qr_scans":len(scans),
            "quiz_attempts":len(quizzes),"quiz_correct":correct,
            "quiz_accuracy":round(correct*100/len(quizzes),1) if quizzes else 0}

@app.get("/api/analytics/devices")
def analytics_devices(db:Session=Depends(get_db)):
    result=[]
    for d in db.query(models.Device).order_by(models.Device.code).all():
        ev=db.query(models.DeviceEvent).filter_by(device_code=d.code).all()
        quiz=[e for e in ev if e.event_type=="QUIZ_ANSWER"]; good=0
        for e in quiz:
            try:
                if json.loads(e.payload or "{}").get("correct"): good+=1
            except Exception: pass
        result.append({"device_code":d.code,"name":d.name,"events":len(ev),
          "qr_scans":sum(e.event_type=="QR_SCAN" for e in ev),"quiz_attempts":len(quiz),
          "correct":good,"accuracy":round(good*100/len(quiz),1) if quiz else 0})
    return result

@app.get("/api/analytics/export.csv")
def analytics_export(db:Session=Depends(get_db)):
    buf=io.StringIO(); w=csv.writer(buf)
    w.writerow(["ID","Ma thiet bi","Loai su kien","Nguon","Thoi gian","Du lieu"])
    for e in db.query(models.DeviceEvent).order_by(models.DeviceEvent.id.asc()).all():
        w.writerow([e.id,e.device_code,e.event_type,e.source,e.created_at.isoformat() if e.created_at else "",e.payload])
    return StreamingResponse(io.BytesIO(buf.getvalue().encode("utf-8-sig")),
      media_type="text/csv; charset=utf-8",
      headers={"Content-Disposition":"attachment; filename=smart_stem_events.csv"})

@app.websocket("/ws/device")
async def websocket_device(ws:WebSocket):
    await hub.connect(ws)
    try:
        while True:
            data=await ws.receive_json()
            await hub.broadcast({"type":"device_event",**data})
    except WebSocketDisconnect: hub.disconnect(ws)

@app.websocket("/ws/ui")
async def websocket_ui(ws:WebSocket):
    await hub.connect(ws)
    try:
        while True: await ws.receive_text()
    except WebSocketDisconnect: hub.disconnect(ws)
