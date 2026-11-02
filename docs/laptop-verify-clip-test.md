# Laptop Verify + Clip Test (W4d4)

Mục tiêu: confirm weight 8-class chạy **realtime** trên laptop TUF F15 (RTX 3050 4GB)
+ pipeline end-to-end (detect → track → distance → gater → alert → HUD) báo đúng
trên clip thật. mAP val chỉ đo detection — bước này mới là ground truth cho mission.

## Weight candidate (trên server, copy sang laptop)

| Weight | Size | soldier mAP50 | Khi nào dùng |
|--------|------|---------------|--------------|
| `weights/yolo26s-military-8c.pt` | 20MB | 0.895 | **Khuyến nghị** (rebal, mission-optimized) |
| `weights/yolo26s-military-8c-base.pt` | 20MB | 0.876 | Fallback (26s base) |
| `weights/yolo26n-military-8c.pt` | 5.2MB | 0.838 | Fallback nhẹ nhất (nếu 26s nặng) |

Transfer: commit weight (trackable — `weights/*.pt` không bị ignore) rồi `git pull`
trên laptop, **hoặc** `scp`/USB copy thẳng file `.pt`.

## Setup laptop (one-time, nếu chưa có)

Windows (PowerShell), trong thư mục project:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install torch==2.14.0 torchvision==0.29.0 --index-url https://download.pytorch.org/whl/cu130
pip install -r requirements-lock.txt
```

> `requirements-lock.txt` pin đúng stack server (AC7) — weight train trên server
> phải load + chạy được trên laptop.

## Chạy clip test

```powershell
# 1) Clip bus 360p có sẵn (khói thuốc pipeline, chưa cần SLM/Ollama)
python heretic_phase4_hud.py --model weights/yolo26s-military-8c.pt --video assets\bus-360p.mp4

# 2) Clip UAV thật của cậu (lính + xe QS) — quan trọng nhất
python heretic_phase4_hud.py --model weights/yolo26s-military-8c.pt --video <clip-cua-cau>.mp4

# 3) Thêm SLM Ollama (nếu Ollama đang chạy) cho câu cảnh báo tiếng Việt
python heretic_phase4_hud.py --model weights/yolo26s-military-8c.pt --video <clip>.mp4 --slm
```

Không cần `--slm` ở lần chạy đầu: gater dùng **template** (0ms, không cần Ollama)
vẫn ra alert banner — đủ verify pipeline. Bật `--slm` sau khi Ollama sẵn.

## Đọc kết quả

- **FPS**: in `[FPS] x.x` mỗi 30 khung.
  - ≥ 15–20 fps → usable cho demo.
  - < 10 fps → 26s nặng: thử `--model weights\yolo26n-military-8c.pt` (nhẹ hơn).
- **Box + label**: lính phải ra `soldier` (KHÔNG phải `person`), xe QS ra `military_vehicle`.
- **Alert banner**: target nguy hiểm trong tầm → banner "CANH BAO: ..." flash 3 khung.
- **Minimap**: dot địch + UAV.
- **person (dân thường)**: KHÔNG được báo (đúng thiết kế).

## Fallback nếu 26s nặng laptop

1. `--model weights\yolo26s-military-8c-base.pt` (cùng size 26s, soldier 0.876)
2. `--model weights\yolo26n-military-8c.pt` (5.2MB, soldier 0.838 — nhẹ nhất)
3. `--cpu` (chạy YOLO trên CPU, nhường VRAM cho SLM) — chậm hơn, chỉ khi VRAM hết

## Known issue (phát hiện smoke test 26/11)

Clip `assets/bus-360p.mp4` (360p) bị model nhận thành **`boat` + `person`**, không
phải `bus` → bus↔boat lẫn lộn ở resolution thấp (dưới 640 train). Khi test clip thật,
ưu tiên footage **≥ 640p** để khớp domain train. Nếu bus/boat lẫn nhiều trên clip thật
→ lever data: thêm data bus+boat rõ ràng, hoặc train imgsz cao hơn.
