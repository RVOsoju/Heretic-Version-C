# Chạy Heretic HUD trên laptop — hướng dẫn (TUF F15, RTX 3050 4GB)

Mục tiêu: confirm weight 8-class chạy **realtime** trên laptop + pipeline end-to-end
(detect → track → distance → gater → alert → HUD) báo đúng trên clip thật.

> **Vì sao phải test trên laptop:** server (4× Ada 32GB) có VRAM nhiều hơn → FPS trên
> server là số **tối ưu**, KHÔNG đại diện realtime. Laptop 4GB mới là ground truth cho
> demo. Test trên server chỉ dùng để verify **pipeline chạy đúng** (label/alert/HUD),
> không phải để đo FPS.

## Bước 0 — Chuẩn bị (cần gì)

- [ ] Laptop Windows + đã cài **NVIDIA driver** (RTX 3050)
- [ ] Project đã `git pull` → có file `weights/yolo26s-military-8c.pt` (20MB)
- [ ] 1 clip test — **ưu tiên footage UAV ≥ 640p** (khớp domain train, tránh bus↔boat)

## Bước 1 — Lấy weight về laptop

**Cách A (khuyến nghị):** weight đã được commit (trackable, `weights/*.pt` không bị
ignore) → chỉ cần `git pull` trong thư mục project.

**Cách B:** `scp` hoặc USB copy thẳng file `weights/yolo26s-military-8c.pt`.

## Bước 2 — Setup venv (one-time, nếu chưa có)

Windows PowerShell, trong thư mục project:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install torch==2.14.0 torchvision==0.29.0 --index-url https://download.pytorch.org/whl/cu130
pip install -r requirements-lock.txt
```

> `requirements-lock.txt` pin đúng stack server → weight train trên server load + chạy
> được trên laptop. Chỉ chạy 1 lần, sau đó bỏ qua bước này.

## Bước 3 — Chạy clip test

```powershell
# 1) Clip 360p có sẵn — verify pipeline chạy (chưa cần Ollama)
python heretic_phase4_hud.py --model weights\yolo26s-military-8c.pt --video assets\bus-360p.mp4

# 2) Clip UAV THẬT của cậu (lính + xe QS) — QUAN TRỌNG NHẤT
python heretic_phase4_hud.py --model weights\yolo26s-military-8c.pt --video <clip-cua-cau>.mp4

# 3) (Tuỳ chọn) thêm SLM Ollama cho câu cảnh báo tiếng Việt — chỉ khi Ollama đang chạy
python heretic_phase4_hud.py --model weights\yolo26s-military-8c.pt --video <clip>.mp4 --slm
```

Không cần `--slm` ở lần chạy đầu: gater dùng **template** (0ms, không cần Ollama) vẫn ra
alert banner — đủ verify pipeline. Bật `--slm` sau khi Ollama sẵn.

## Bước 4 — Đọc kết quả

| Xem gì | Đạt khi |
|--------|---------|
| **FPS** (`[FPS] x.x` in mỗi 30 khung) | ≥ 15–20 fps = usable cho demo; < 10 fps = 26s nặng → xem Fallback |
| **Box + label** | lính ra `soldier` (KHÔNG phải `person`), xe QS ra `military_vehicle` |
| **Alert banner** | target nguy hiểm trong tầm → "CANH BAO: ..." flash 3 khung |
| **Minimap** | dot địch + vị trí UAV |
| **person (dân thường)** | **KHÔNG** được báo (đúng thiết kế) |

## Fallback nếu 26s nặng laptop

1. `--model weights\yolo26s-military-8c-base.pt` (cùng size 26s, soldier 0.876)
2. `--model weights\yolo26n-military-8c.pt` (5.2MB, soldier 0.838 — nhẹ nhất)
3. `--cpu` (YOLO chạy CPU, nhường VRAM cho SLM) — chậm hơn, chỉ khi VRAM hết

## Weight candidate

| Weight | Size | soldier mAP50 | Khi nào dùng |
|--------|------|---------------|--------------|
| `weights/yolo26s-military-8c.pt` | 20MB | 0.895 | **Khuyến nghị** (rebal, mission-optimized) |
| `weights/yolo26s-military-8c-base.pt` | 20MB | 0.876 | Fallback (26s base) |
| `weights/yolo26n-military-8c.pt` | 5.2MB | 0.838 | Fallback nhẹ nhất (nếu 26s nặng) |

## Known issue (smoke test 26/11)

Clip `assets/bus-360p.mp4` (360p) bị nhận thành **`boat` + `person`**, không phải `bus`
→ bus↔boat lẫn ở resolution thấp (dưới 640 train). Khi test clip thật, ưu tiên footage
**≥ 640p** để khớp domain train. Nếu bus/boat lẫn nhiều trên clip thật → lever data:
thêm data bus+boat rõ, hoặc train imgsz cao hơn.
