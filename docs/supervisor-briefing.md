# Heretic Version C — Báo Cáo Trình Bày Cho Giảng Viên Hướng Dẫn

**Ngày:** 2026-10-12 · **Thời lượng dự kiến:** 10–15 phút
**Tài liệu chi tiết đi kèm:** `project-overview-pdr.md` (scope + tiêu chuẩn nghiệm thu) ·
`battlefield-realism-architecture-report.md` (phân tích kiến trúc đầy đủ)

---

## 1. Dự án trong 1 đoạn

Heretic C là **hệ thống HUD chiến thuật phi sát thương** cho lính: nhận video trinh sát
từ UAV/webcam → phát hiện + theo dõi mục tiêu (YOLO) → phân biệt địch/đồng đội qua GPS →
cảnh báo qua 3 kênh: **hình** (bounding box quân dụng + minimap), **rung im lặng**
(haptic — OPSEC, không lộ vị trí), và **câu chữ AI** (SLM tiếng Việt, cho màn chỉ huy).
Chạy thời gian thực trên laptop cá nhân (RTX 3050 4GB), liên kết UAV qua **LoRa riêng**
— không phụ thuộc hạ tầng WiFi dân dụng. Kịch bản: **1 lính + 1 UAV**.

## 2. Target & scope (tóm tắt — chi tiết trong PDR)

- **Mục đích:** demo/đồ án đạt **70–80% sát thực tế chiến trường**.
- **Definition of done = Phase 5:** tracking (track ID ổn định, tốc độ tiếp cận) +
  cảnh báo haptic + link LoRa + UAV tuần tra có vùng phủ + YOLO nâng từ 6 class COCO
  lên 8 class (fine-tune trên dataset quân sự MVRSD, thêm xe tăng/xe bọc thép).
- **Mỗi mục scope gắn 1 acceptance criteria đo được** (PDR §5, AC1–AC11) — ví dụ:
  track ID re-ID <5% trên 100 khung; cảnh báo haptic <200ms và không phát âm;
  mAP50 ≥0,75 trên val MVRSD; VRAM <3,8GB; demo end-to-end 10 phút không interrupt.
- **Stretch (nếu có tài trợ 5–8M):** Phase 6 — camera thermal ban đêm (FLIR Lepton 5)
  + mesh đa lính + node lính độc lập (ESP32-S3 client hoặc tablet Jetson Orin Nano).

## 3. Đã hoàn thành (có bằng chứng)

| Thành phần | Trạng thái | Bằng chứng |
|------------|-----------|------------|
| Pipeline YOLO26n → gater 100/10/1m → SLM → HUD | Chạy được, 6 class nguy hiểm (person + xe) | `heretic_phase4_hud.py`, chế độ `--sim` xuất 16 khung ảnh |
| SLM qwen2.5:3b (Ollama) cảnh báo tiếng Việt ≤12 từ | Latency đã đo: floor ~0,4s (server), ước 0,8–1,5s (laptop) | `tactical_slm.py --demo` |
| HUD quân dụng: bbox + minimap + địch/đồng đội theo GPS (bán kính 8m) | Hoàn thành | `tactical_hud_renderer.py` |
| Chuỗi telemetry UAV: ESP32 + GPS NEO-6M → UDP 1Hz → HUD | **11/11 kiểm thử PASS** (kèm ảnh minh chứng) | `test_telemetry_chain.py` |
| Tối ưu cho laptop 4GB VRAM (chạy thật, không phải server) | Dual-mode GPU/CPU (`--cpu`), warmup SLM, guide cài đặt Windows 11 | `laptop-deployment-guide.md` |

**Điểm trung thực (không che):** khoảng cách hiện tại là ước tính scale pixel (±30–50%),
chưa có track ID, chưa hoạt động ban đêm, link đang là UDP/WiFi (chưa phải LoRa) —
đây chính là các mục Phase 5/6 ở trên.

## 4. Kiến trúc (5 nguyên tắc — chi tiết trong báo cáo kiến trúc)

1. **Quyết định ở edge** — node lính tự quyết "tôi bị đe dọa" cục bộ, không chờ trạm chỉ huy.
2. **Trạm chỉ huy (laptop) là optional** — mất nó, lính vẫn có cảm biến + cảnh báo cục bộ.
3. **Mọi link đều có thể đứt** — 3 chế độ: đầy đủ / suy giảm (chỉ LoRa vị trí) / cục bộ;
   dữ liệu cũ >5s bị vô hiệu (cơ chế đã có trong code).
4. **Mô hình dữ liệu thống nhất: Track** `{id, pos, vel, class, side, confidence, ttl}`
   → thay transport UDP→LoRa không đụng giao diện.
5. **AI text chỉ advisory** — SLM (0,4–1,5s) cho màn chỉ huy, **không** nằm trong vòng lặp <100ms.

Lưu lượng hệ thống rất nhỏ (~30 byte/s/node) → LoRa mesh 1–5km **đủ**, không cần hạ tầng.

## 5. Kế hoạch & ngân sách (Phase 5 — 2–3 tuần)

| Mốc | Nội dung |
|-----|----------|
| M1 (tuần 1) | Tracking + haptic + gater theo track ID |
| M2 (tuần 1–2) | Fine-tune YOLO 8 class trên MVRSD (GPU server) |
| M3 (tuần 2) | Link LoRa (thay UDP transport, giữ interface) |
| M4 (tuần 2–3) | UAV tuần tra + FOV + demo end-to-end (flycam E88 Pro) |

**Ngân sách phần cứng Phase 5: ~3–5M VND** — LoRa ×3 (300–450k), module rung (50–150k),
flycam E88 Pro + receiver (2–4M, verify giá). Phase 6 (thermal + mesh): +5–8M nếu tài trợ.

## 6. Rủi ro chính

| Rủi ro | Mitigation |
|--------|------------|
| Dataset MVRSD tải qua Baidu — server có thể không truy cập | Verify tuần 1; fallback: dataset GitHub (AMAD, InvictusRex) |
| Fine-tune làm degrade 6 class COCO cũ | Fine-tune trộn MVRSD + COCO; đo mAP cả 2 tập |
| Flycam E88 Pro: receiver chưa confirm có USB capture | Verify trước khi mua |
| Nhiệt/VRAM khi chạy full trên laptop 4GB | Chế độ `--cpu` dự phòng đã có |

## 7. Câu hỏi cần ý kiến giảng viên

1. Scope Phase 5 (8 class, LoRa, haptic, UAV tuần tra) có phù hợp làm **vòng chốt đồ án** không?
2. Dataset MVRSD (xe quân sự, 3.000 ảnh) — chấp nhận nguồn dataset nước ngoài cho fine-tune?
3. Frequence LoRa 915MHz cho demo tại VN — có cần chuyển 868MHz (band Meshtastic phổ biến) không?
4. Với định hướng demo 70–80% thực tế, có nên ưu tiên thêm **camera thermal** (ban đêm) vào scope thay vì một phần mục khác?

## 8. Danh mục tài liệu

| File | Nội dung |
|------|----------|
| `project-overview-pdr.md` | Target, scope IN/OUT, 11 acceptance criteria, BOM, mốc |
| `battlefield-realism-architecture-report.md` | Phân tích gap 8 điểm, kiến trúc edge-first, 3 tier nâng cấp |
| `hardware-bom.md` | BOM chi tiết 3 node, sơ đồ đấu flycam, spec firmware ESP32 |
| `laptop-deployment-guide.md` | Cài đặt + 7 bước kiểm thử trên laptop TUF F15 (Windows 11) |
