import {useEffect,useState} from 'react';
import {Cpu,Network,HardDrive,MemoryStick,QrCode,RefreshCw,Monitor,Wifi,Box,PlayCircle} from 'lucide-react';
const API=(import.meta as any).env.VITE_API_URL || `http://${location.hostname}:8000`;
type Device={id:number;code:string;name:string;description:string;function:string;module_id:number;qr_path:string;model3d_path:string;video_path:string;image_path:string};
const icons=[Cpu,Network,HardDrive,MemoryStick];
export default function App(){
 const [devices,setDevices]=useState<Device[]>([]),[modules,setModules]=useState<any[]>([]),[selected,setSelected]=useState<Device|null>(null),[status,setStatus]=useState('Đang kết nối...');
 async function load(){try{const [d,m]=await Promise.all([fetch(API+'/api/devices'),fetch(API+'/api/modules')]);setDevices(await d.json());setModules(await m.json());setStatus('Máy chủ đã kết nối')}catch{setStatus('Chưa kết nối máy chủ')}}
 useEffect(()=>{load();const ws=new WebSocket(API.replace('http','ws')+'/ws/ui');ws.onmessage=e=>{const x=JSON.parse(e.data);if(x.type==='device_event'){const d=devices.find(v=>v.code===x.device_code);if(d)setSelected(d)}};return()=>ws.close()},[]);
 async function qrAll(){const r=await fetch(API+'/api/qr/generate-all?request_base='+encodeURIComponent(API),{method:'POST'});if(r.ok){await load();alert('Đã tạo QR cho danh sách thiết bị.')}} 
 const modNames=['Phần cứng máy tính','Thiết bị mạng','Điều khiển và mô phỏng','Học tập số'];
 return <div className="app"><header><div><div className="eyebrow">INTERACTIVE 3D COMPUTER LAB</div><h1>SMART STEM <span>CONTROL CENTER</span></h1><p>Mô hình khám phá máy tính và mạng máy tính thông minh</p></div><div className="status"><span className="dot"/>{status}</div></header>
 <section className="hero"><div><h2>Trung tâm điều khiển mô hình STEM</h2><p>Quản lý thiết bị, mã QR và nội dung học tập trên một nền tảng.</p><button onClick={qrAll}><QrCode size={17}/> Tạo QR tất cả thiết bị</button></div><Monitor size={76}/></section>
 <div className="stats"><div><b>{modules.length}</b><span>Mô-đun</span></div><div><b>{devices.length}</b><span>Thiết bị</span></div><div><b>{devices.filter(d=>d.qr_path).length}</b><span>Đã có QR</span></div><div><b>V0.1</b><span>Phiên bản</span></div></div>
 <h2 className="section">Danh mục thiết bị</h2><div className="layout"><main className="devicegrid">{devices.map((d,i)=>{const Icon=icons[i%4];return <article className={'device '+(selected?.code===d.code?'active':'')} key={d.code} onClick={()=>setSelected(d)}><div className="deviceicon"><Icon/></div><div className="code">{d.code}</div><h3>{d.name}</h3><p>{d.description}</p><small>{d.qr_path?'Đã tạo mã QR':'Chưa tạo QR'}</small></article>})}</main>
 <aside><h2>Chi tiết thiết bị</h2>{selected?<><div className="code">{selected.code}</div><h3>{selected.name}</h3><p>{selected.function}</p>{selected.qr_path&&<img className="qr" src={API+selected.qr_path}/>}<p className="muted">Đường dẫn truy cập: {API+'/d/'+selected.code}</p><button onClick={()=>window.open(API+'/d/'+selected.code,'_blank')}>Mở trang thiết bị</button></>:<p className="muted">Chọn một thiết bị để xem thông tin.</p>}<hr/><h3>Kết nối</h3><p><Wifi size={15}/> WiFi / LAN</p><p><Box size={15}/> Thư viện 3D: giai đoạn tiếp theo</p><p><PlayCircle size={15}/> Video: giai đoạn tiếp theo</p><button className="secondary" onClick={load}><RefreshCw size={16}/> Làm mới dữ liệu</button></aside></div>
 <footer>SMART COMPUTER & NETWORK STEM 2.0 · CONTROL CENTER V0.1</footer></div>
}
