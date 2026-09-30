# Hướng Dẫn Chạy Trên Laptop — Heretic Version C

**Target runtime:** Asus TUF F15 FX507 — RTX 3050 (4 GB VRAM), i7-12700H, 16 GB DDR4.
Server (4× RTX 5000 Ada) chỉ dùng để phát triển — hệ thống **phải** chạy mượt trên laptop.
Ngày cập nhật: 2026-09-30

## 1. Ngân sách VRAM 4 GB (vấn đề quan trọng nhất)

| Thành phần | VRAM ước tính |
|------------|---------------|
| Ollama + qwen2.5:3b (Q4) | ~2,3 GB |
| YOLO yolo26n @ 720p (CUDA) | ~1,0–1,5 GB |
| Hệ điều hành + ứng dụng khác | ~0,5–1,0 GB |
| **Tổng (cả hai trên GPU)** | **~4,0–4,8 GB → có thể OOM** |

**Chiến lược:**

1. **Mặc định:** cả YOLO + SLM chạy GPU. Đóng trình duyệt / app nặng trước khi demo (accelerator graphics ăn VRAM).
2. **Khi bị OOM** (torch báo `CUDA out of memory`, hoặc SLM chậm đột biến 2–4 s vì Ollama tụt một phần layer xuống CPU): chạy thêm flag `--cpu` → YOLO chạy trên i7 (vẫn ~8–15 fps, đủ cho HUD vì SLM mới là nhịp bottleneck ~1 s/lần cảnh báo).
3. Không hạ model SLM xuống 1B — 3B đã là mức tối thiểu để giữ chất lượng câu cảnh báo tiếng Việt.

## 2. Cài đặt (Windows 11 — hệ điều hành dự kiến của laptop)

```powershell
# 1) Ollama — installer bản native tự phát hiện GPU (KHONG can workaround port 11435 như trên server)
winget install Ollama.Ollama        # hoặc tải từ ollama.com
ollama pull qwen2.5:3b

# 2) Python + thư viện
git clone https://github.com/RVOsoju/Heretic-Version-C
cd Heretic-Version-C
python -m venv .venv
.venv\Scripts\activate
pip install ultralytics opencv-python numpy requests pyserial

# 3) Tải model YOLO (tự chạy lần đầu, ~10 MB)
python heretic_phase4_hud.py
```

> **Khác biệt với server:** trên laptop Ollama native nghe port **11434** = đúng default của code
> → **KHÔNG cần đặt `OLLAMA_HOST`**. Biến này chỉ dùng trên máy dev (server).

## 3. Các lệnh kiểm thử (theo thứ tự)

| # | Lệnh | Mục đích | KPI chấp nhận |
|---|------|----------|---------------|
| 1 | `ollama run qwen2.5:3b "Tra ve 1 tu: An toan"` | SLM sống, chạy GPU | trả lời < 2 s |
| 2 | `python tactical_slm.py --demo` | Chuỗi cảnh báo SLM | mỗi câu < ~1,5 s |
| 3 | `python heretic_phase4_hud.py --sim` | HUD + SLM, không cần webcam | 16 ảnh `sim_hud_*.png`, cảnh báo đúng nhịp |
| 4 | `python test_telemetry_chain.py` | Chuỗi telemetry UDP | 11/11 PASS |
| 5 | `python heretic_phase4_hud.py` | **Full live** (webcam) | HUD mượt, cảnh báo khi có người vào trong 100 m |
| 6 | `python heretic_phase4_hud.py --telemetry --gps-port COM5` | Full + GPS (khi có phần cứng) | chấm đồng đội hiện trên minimap |

**Giám sát VRAM khi chạy #5:** mở terminal thứ hai, chạy `nvidia-smi -l 1` —
VRAM dùng < ~3,8 GB là an toàn; chạm trần 4 GB là nên bật `--cpu` (lệnh #7).

| 7 | `python heretic_phase4_hud.py --cpu` | Chế độ dự phòng OOM | YOLO trên CPU, SLM giữ GPU |

## 4. Hiệu năng kỳ vọng (thực tế, không đẹp hoá)

| Thành phần | GPU (RTX 3050) | CPU (i7-12700H) |
|------------|----------------|-----------------|
| YOLO yolo26n @ 720p | ~20–40 fps | ~8–15 fps |
| SLM qwen2.5:3b, 1 câu cảnh báo | ~0,8–1,5 s | ~3–5 s |

- Mục tiêu < 0,2 s cho SLM **không đạt được trên bất kỳ máy nào** qua Ollama HTTP
  (đã đo trên server: floor ~0,4 s) — cảnh báo có delay ~1 s trên laptop,
  chấp nhận được vì gater chỉ bắn cảnh báo cách quãng (mỗi 10 m / 1 m).
- Nếu sau này yêu cầu cứng < 0,2 s: thay Ollama bằng llama.cpp `llama-server`
  (không đổi interface `call_ollama` nhiều — chỉ đổi URL payload).

## 5. Checklist trước khi demo

- [ ] Ollama chạy + `ollama list` thấy qwen2.5:3b
- [ ] `--sim` chạy xong, xem lại 2–3 ảnh `sim_hud_*m_alert.png`
- [ ] Live: warmup SLM in `[INFO] SLM da nong` trước khi vào vòng lặp (code tự làm)
- [ ] `nvidia-smi -l 1` quan sát 30 s đầu — VRAM ổn không?
- [ ] Cắm webcam trước, kiểm tra `cv2.VideoCapture(0)` mở được (lệnh #5 tự in khi break)
- [ ] (Có GPS) `--gps-port` đúng tên COM, `--telemetry` bật, có tín hiệu UDP từ ESP32

## 6. Khắc phục sự cố nhanh

| Triệu chứng | Nguyên nhân | Xử lý |
|-------------|-------------|-------|
| `CUDA out of memory` (torch) | YOLO + SLM cùng chiếm VRAM | Thêm `--cpu` |
| SLM đột nhiên 2–4 s/câu | Ollama push layer xuống CPU do thiếu VRAM | Đóng app nặng / thêm `--cpu` |
| `[CANH CAO] SLM chua san sang` | Ollama chưa chạy | `ollama serve` (Windows: icon Ollama trên tray) |
| `cv2.VideoCapture(0)` fail | Chưa cắm webcam / app khác đang giữ | Cắm lại, đóng camera app |
| GPS `None` | Chưa có fix / sai COM | Ra ngoài trời 30 s / đổi `COMx` |
| Chấm UAV không hiện | ESP32 chưa phát UDP / IP đổi | Kiểm tra DHCP reservation, port 8888 |
