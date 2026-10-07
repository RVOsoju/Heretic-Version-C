# Báo Cáo Kiến Trúc — Hướng "70–80% Thực Tế Chiến Trường"

**Dự án:** Heretic Version C — HUD chiến thuật cho lính (YOLO + SLM Ollama + HUD + telemetry GPS)
**Ngày:** 2026-10-01
**Trạng thái:** Đề xuất — làm cơ sở quyết định phase tiếp theo
**Cập nhật 2026-10-07:** Tier A2 (TTS giọng nói) bị thay bằng **haptic rung im lặng** (OPSEC) — scope hiện hành xem [project-overview-pdr.md](project-overview-pdr.md)
**Runtime target:** Laptop Asus TUF F15 (RTX 3050 4GB VRAM, i7-12700H, 16GB RAM)
**Giả định liên kết:** "không có WiFi" = không có hạ tầng dân dụng; **được phép dựng link riêng** (LoRa/mesh/FPV)

---

## 1. Tóm tắt điều hành

- Hệ thống hiện tại ở mức **demo để bàn ~30–40%** thực tế chiến trường.
- Ba nhóm gap chính: **(1) cảm biến** (không ban đêm, không tracking, khoảng cách là ước tính), **(2) liên kết dữ liệu** (phụ thuộc WiFi/UDP), **(3) kiến trúc** (laptop-centric — laptop chết là hệ thống chết).
- Khuyến nghị: **không nhảy tới 100%**. Đi "nhân thực tế" (Hướng 1: tracking + âm thanh + LoRa + UAV tuần tra) → đạt 60–70% với ~500k–1M VND.
- Tính ứng dụng trung thực: **huấn luyện/mô phỏng = giá trị cao nhất**; demo/đồ án = cao; **triển khai thật = ngoài khả năng ngân sách hiện tại**.
- Điểm mạnh cốt lõi: hệ thống **phi sát thương** (chỉ phát hiện + cảnh báo) — không vướng vấn đề vũ khí tự động.

## 2. Baseline hiện tại — thông tin chiến thuật hệ thống đang cho

| Thông tin | Nguồn | Độ chính xác | Độ trễ |
|-----------|-------|--------------|--------|
| Mục tiêu (person/xe) + bounding box | YOLO26n | Ban ngày tốt; **ban đêm/rain/khói: không** | 20–40 fps (GPU 3050) |
| Khoảng cách | Scale pixel (0,05 m/px) | **Ước tính, sai ±30–50%, KHÔNG phải đo** | Cùng khung |
| Hướng | 4 phương (Đ/B/T/N) | Lượng tử hóa 45° | Cùng khung |
| Địch/đồng đội | GPS tươi <5s, bán kính 8m | Phụ thuộc fix GPS | 1 Hz |
| Câu cảnh báo | SLM qwen2.5:3b (Vietnamese, ≤12 từ) | Tốt, deterministic (temp 0) | 0,4–1,5 s/call, chỉ khi gater cho (100/10/1m) |
| Vị trí UAV | ESP32 + NEO-6M qua UDP | NEO-6M ±3–5 m | 1 Hz |
| Minimap | Renderer OpenCV | Bán kính 100 m | 20–40 fps |

**8 điểm yếu so với chiến trường thật:**

1. **Không có track ID** — gater key theo `(target, bearing)`: mục tiêu di chuyển làm key nhảy → cảnh báo lặp/thiếu.
2. **Chỉ RGB** — không hoạt động ban đêm (kịch bản chiến thuật quan trọng nhất).
3. **Không kênh âm thanh** — mắt lính nhìn kính ngắm, không nhìn màn hình.
4. **Link WiFi/UDP** — môi trường tác chiến không có hạ tầng này.
5. **Laptop-centric** — single point of failure.
6. **Khoảng cách ước tính** — đủ cảnh báo, không đủ quyết định.
7. **UAV bay tay** — không có logic tuần tra, không hiển thị vùng phủ camera.
8. **Nguồn điện** — pin laptop 30–60 phút.

## 3. Phân tích gap theo cấp độ

### Tier A — "phải có" cho 70% (hiệu quả cao / chi phí thấp)

| # | Thành phần | Chi tiết | Chi phí ước |
|---|------------|----------|-------------|
| A1 | **Tracking (ByteTrack)** | Chạy real-time trên CPU; identity ổn định giữa các khung; tính được **vận tốc & tốc độ tiếp cận**; gater chuyển sang key theo `track_id` | ~0 (thư viện mở) |
| A2 | **Âm thanh TTS** | espeak-ng/pyttsx3; "CẢNH BÁO: kẻ địch 12 mét, hướng tây" — kênh chính khi mắt ở kính ngắm | ~0 |
| A3 | **Link LoRa riêng** | RFM95/M5Stack 915MHz; 1–5 km; layer vị trí chuyển UDP→LoRa; **interface `TelemetryFeed` giữ nguyên** | 300k–450k (×3 module + anten) |
| A4 | **UAV tuần tra + FOV** | Flycam bay theo waypoints; laptop vẽ vùng phủ camera lên minimap | 0 (code) |

### Tier B — "nên có" cho 80% (chi phí trung bình, hiệu quả cao)

| # | Thành phần | Chi tiết | Chi phí ước |
|---|------------|----------|-------------|
| B1 | **Thermal FLIR Lepton 5** | USB, 160×120; model phát hiện nhiệt có sẵn của FLIR; dual-stream RGB+IR → **ban đêm hoạt động được** | 4–6M (ước tính 2026) |
| B2 | **Mesh đa lính** | Mỗi node lính 1 module LoRa; chia sẻ Track qua mesh (Meshtastic) | +2 module (đã tính A3) |
| B3 | **Nguồn điện field** | Powerbank 10–20000mAh ×2, plan chạy theo giờ | 600k–1M |
| B4 | **Khoảng cách trung thực** | <30m: stereo/ToF; >30m: **công khai là ước tính** (không có magic ở mức laptop) | 1–3M (tuỳ chọn) |

### Tier C — cho prototype thật (ngân sách lớn, 1–2 năm)

- Node lính độc lập (RPi 5/Jetson, rugged, màn head-mounted)
- NPU trên UAV (Jetson Nano): **pre-detection** → gửi track (dữ liệu nhỏ), video chỉ cho mắt người → tiết kiệm bandwidth, tăng tốc
- Mật mã/anti-jam (LoRa AES-128, frequency hopping)
- Retrain YOLO trên dataset quân sự (COCO classes là dân sự)

## 4. Kiến trúc đề xuất (trọng tâm)

**Từ laptop-centric sang edge-first + degradation-tolerant.**

```
                        ┌──────────────────────────────┐
                        │    LAPTOP = C2 (chỉ huy)     │
                        │  YOLO + SLM + HUD + bản đồ   │
                        └──────▲────────────────▲──────┘
                    video FPV 5.8GHz       LoRa 1Hz (position/track)
                        ┌──────┴───────┐   ┌────┴─────────┐
                        │   UAV        │   │  LÍNH A      │
                        │ cam + GPS    │   │ (laptop /     │
                        │ + LoRa beacon│   │  RPi + màn)  │
                        └──────────────┘   └────┬─────────┘
                                             LoRa mesh
                                             ┌────┴─────┐
                                             │  LÍNH B   │
                                             └───────────┘
```

**5 nguyên tắc:**

1. **Quyết định ở edge** — node lính tự quyết "tôi bị đe dọa" cục bộ, không chờ C2 (C2 có thể chết).
2. **C2 là optional** — laptop = màn hình lớn + SLM tổng hợp, **không nằm trong vòng lặp thời gian thực** của lính.
3. **Mọi link đều có thể đứt** — 3 chế độ vận hành: *đầy đủ* (mesh + video) / *suy giảm* (chỉ LoRa vị trí) / *cục bộ* (chỉ cảm biến của mình). `last-known` + TTL 5s **đã có sẵn trong code** (`STALE_AFTER_S`).
4. **Mô hình dữ liệu thống nhất: Track** `{id, pos, vel, class, side, confidence, ttl}` — HUD render từ track, không từ box thô → thay transport UDP→LoRa **không đụng UI**.
5. **SLM chỉ advisory** — câu chữ cho C2 (0,4–1,5s), **không** trong vòng lặp <100ms.

**"Thời gian thực" của lính = hình ảnh (box màu + mũi tên) + âm thanh, 20–40 fps cục bộ.**
AI text là "lớp cho bộ não" của người chỉ huy trên màn C2 — không phải kênh cảnh báo chính.

## 5. Luồng dữ liệu — trả lời 4 câu hỏi cốt lõi

### 5.1. Dữ liệu trinh sát UAV lấy từ đâu?

- **Video:** camera flycam → link FPV 5,8GHz (LOS 1–3 km) → laptop (ground station) → YOLO.
- **Vị trí:** NEO-6M → ESP32 → beacon LoRa 1Hz → C2.
- **Tương lai (Tier C):** NPU trên UAV pre-detect → chỉ gửi track (vài trăm byte/s); video giữ cho mắt người.

### 5.2. Không có WiFi thì dữ liệu xây ra sao?

Insight chính: **lưu lượng dữ liệu của hệ thống này cực nhỏ** (vị trí ~30 byte/s/node; track ~100–200 B/s) → **LoRa mesh hoàn toàn đủ**, không cần hạ tầng, không router, không SIM, tầm 1–5 km địa hình mở.

- Layer vị trí/track: **LoRa 1Hz** — LoRa dư sức.
- Video: LoRa không gánh được → **FPV 5,8GHz** (LOS) hoặc optical/IR (Tier C).
- Link đứt hoàn toàn → **chế độ cục bộ**: mỗi node dùng cảm biến của mình, TTL 5s cho dữ liệu chung (cơ chế đã có), hệ không crash.
- Kết luận: "không có WiFi dân dụng" **không chặn** hệ thống. Chỉ trường hợp "môi trường chống RF/jamming toàn phần" mới buộc chạy chế độ cục bộ.

### 5.3. Thông tin chiến thuật nhận được (sau nâng cấp)?

Track ổn định (ID không nhảy) + khoảng cách (+tốc độ tiếp cận) + hướng mịn 360° + địch/đồng đội + **ban đêm (thermal)** + **cảnh báo giọng nói** + bản đồ C2 có vùng phủ UAV.

### 5.4. Thời gian thực kết hợp AI ra sao?

| Lớp | Latency | Vai trò |
|-----|---------|---------|
| Detection + tracking | 20–40 fps, <30ms, local | Kênh chính (hình ảnh) |
| Đánh giá đe doạ (gater + track) | <10ms, deterministic | Quyết định có báo không |
| Âm thanh TTS | <200ms | Kênh thứ 2 (mắt ở kính ngắm) |
| SLM (câu cảnh báo) | 0,4–1,5s, chỉ khi gater cho | Advisory cho C2 |

## 6. Thay đổi phần cứng (delta so với hardware-bom.md)

| Linh kiện | SL | Giá ước (2026) | Tier | Mục đích |
|-----------|----|----------------|------|----------|
| LoRa RFM95/M5Stack 915MHz + anten | 3 | 300k–450k | A | Link vị trí/track: UAV + 2 lính |
| FPV TX 5,8GHz (nếu flycam chưa có) | 1 | 300k–500k | A | Video downlink UAV→C2 |
| FLIR Lepton 5 + mount | 1 | 4–6M | B | Ban đêm |
| Powerbank 10–20000mAh | 2 | 600k–1M | B | Nguồn field |
| Jetson Nano (UAV) | 1 | 3–5M | C | Pre-detection |
| RPi 5 8GB (node lính) | 1 | 2,5–3,5M | C | Node độc lập cho lính |

*Giá là ước tính — cần verify giá 2026 khi đặt mua.*

## 7. Đánh giá tính ứng dụng TRUNG THỰC (quan trọng nhất)

| Mục đích | Giá trị | Lý do |
|----------|---------|-------|
| **Huấn luyện / mô phỏng** | **CAO — khuyến nghị làm trục chính** | Thao trường = môi trường kiểm soát (không jamming, có hạ tầng) → Tier A+B đạt đúng 70–80% yêu cầu. Lính tập đọc HUD, phản ứng cảnh báo, phân biệt địch/đồng đội. Giá trị/VND cao nhất |
| **Demo / đồ án** | CAO | Pipeline sensing→AI→HUD→SLM hoàn chỉnh; SLM tiếng Việt là differentiator thật; 70–80% "độ thật" của demo đạt được trên laptop + LoRa + tracking + audio |
| **Triển khai thật** (cảnh giới/base) | THẤP ở ngân sách hiện tại | Gap: ban đêm, anti-jam, rugged, dataset quân sự, nguồn điện >2h. Thực tế: 1–2 năm R&D + ngân sách chục triệu–hàng trăm triệu |

**Điểm mạnh có thể bảo vệ (defensible):**

- **Phi sát thương** (chỉ phát hiện + cảnh báo) — hợp lệ về pháp lý/đạo đức, là sản phẩm "tình báo–cảnh báo" (situational awareness), không phải vũ khí tự động.
- **AI cục bộ ở edge** — mất C2 không mất năng lực sống còn của lính.
- **Nhận diện địch/đội bằng GPS** — đơn giản, hiệu quả trong phạm vi <~50m, không cần RF ID phức tạp.

**Điểm yếu (không giả vờ không thấy):**

- Khoảng cách là ước tính ±30–50% — đủ cảnh báo, **không đủ để quyết định bắn**.
- YOLO COCO fail ở: CQB <10m, ban đêm (không thermal), nhóm mục tiêu di chuyển nhanh.
- SLM 0,4–1,5s — mục tiêu 0,2s **không đạt được** (đã đo: floor ~0,4s qua Ollama API ngay trên server).
- Laptop = single point of failure cho tới Tier C.

## 8. Lộ trình khuyến nghị

| Phase | Nội dung | Độ "thật" | Chi phí | Thời gian |
|-------|----------|-----------|---------|-----------|
| **Phase 5 — "Nhân thực tế"** | A1 tracking + A2 TTS + A3 LoRa + A4 UAV patrol | 60–70% | 500k–1M | 2–3 tuần |
| **Phase 6 — "Đêm + Mesh"** | B1 Lepton + B2 mesh đa lính + B3 nguồn điện | 75–80% | +5–8M | 1–2 tháng |
| **Phase 7 (tuỳ chọn) — "Phân tán"** | C: node RPi/Jetson, mesh full, NPU UAV | 85%+ | +30M | 2–3 tháng |

Tăng trưởng increment trên kiến trúc hiện có: `TrackStore` (thay dict của `TelemetryFeed`) là **điểm hội tụ duy nhất** — HUD/SLM không đổi.

## 9. Câu hỏi mở

1. Flycam dự định **đã có sẵn FPV video TX 5,8GHz** chưa? (quyết định chi phí video downlink)
2. Kịch bản có **bao nhiêu lính** (1 lính + UAV, hay tốp 3–5)? → quy mô mesh.
3. Ngân sách có trần cho Tier B (thermal ~4–6M VND) không?
4. Chốt trục ứng dụng là **"huấn luyện/mô phỏng"** theo §7 không?
