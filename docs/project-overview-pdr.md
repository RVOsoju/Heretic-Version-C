# PDR — Heretic Version C: Target, Scope & Acceptance Criteria

**Dự án:** HUD chiến thuật cho lính — YOLO + cảnh báo tiếng Việt (template + SLM Ollama optional) + HUD + telemetry UAV
**Ngày:** 2026-10-07 · **Cập nhật:** 2026-10-26 (W2 xong → **M1 done**: object-height anchor — sim 30m sai 1.2–1.3%; flash HUD 3 khung @30fps (AC4); AC1 re-ID 0.0%/150 khung; AC2 vận tốc sai 1.2%; AC3 1 cảnh báo/ngưỡng — `test_tracking.py` 7/7 + telemetry 20/20) · **B9 (nguồn `soldier`) có 2 nguồn cụ thể do user tìm 26/10: Mendeley ~8k (bird's-eye, YOLO format) + Roboflow ~4.8k — verify W3d3 (license + spot-check label + tham số thu)** · 2026-10-23 (UAV demo: **i1 Pro** đã có (chim tập) + **DJI Mini 2 SE** (demo chính — GPS + áp kế + gimbal 1080P, user mua riêng); downlink = WiFi → app phone → scrcp; W7 tam giác phân GPS giữ nguyên) · 2026-10-19 (kênh câu chữ: **template là chính** (0ms, 0 VRAM) + **SLM optional** `--slm` — giải phóng ~2GB VRAM, không phụ thuộc Ollama) · 2026-10-16 (feedback giảng viên: **dataset góc UAV** + **UAV theo dõi mục tiêu** + **FOV indicator** + **khoảng cách target→lính = tam giác phân GPS** (W7) + **object-height anchor** (W2) — UAV bay vòng quanh lính, không bay trên đầu; 2026-10-15: không tài trợ, mạng riêng WiFi/4G+VPN, UAV được cấp 360P+ — **chưa rõ ngày về**, 8 class chốt: person/soldier + 5 xe thường + military_vehicle)
**Runtime target:** Asus TUF F15 FX507 — RTX 3050 (4GB VRAM), i7-12700H, 16GB DDR4, **Windows 11**
**Kịch bản:** 1 lính + 1 UAV. Phi sát thương — chỉ phát hiện + cảnh báo, không vũ khí tự động.

> **GIẢ ĐỊNH 2026-10-15: KHÔNG CÓ TÀI TRỢ** — chỉ dùng thiết bị có sẵn:
> laptop TUF F15, server dev (4× RTX 5000 Ada — fine-tune), UAV demo (xem dưới).
> Mọi phần cứng mua mới (LoRa, E88 Pro, module rung, Lepton) = **BLOCKED** cho tới khi user báo phần cứng mới.
> **UAV demo (cập nhật 2026-10-23):** **i1 Pro** (mini drone 360–480P, WiFi → app phone,
> không GPS/MAVLink — chim tập, đã có tay) + **DJI Mini 2 SE** (249g, **GPS + áp kế + gimbal
> 1080P**, bay 31 phút — demo chính, user mua riêng; downlink = DJI Fly (app phone) →
> **scrcp USB → laptop**; MAVLink giới hạn qua **DJI Virtual Port**). UAV "được cấp" (nếu về)
> = lựa chọn thay thế.

---

## 1. Target (mission statement)

Heretic C là **hệ thống cảnh báo chiến thuật demo/đồ án đạt 70–80% sát thực tế**:
từ video trinh sát (UAV 360P+/webcam), hệ thống phát hiện + theo dõi mục tiêu, phân biệt
địch/đồng đội qua GPS, và cảnh báo lính qua 3 kênh — hình (box + minimap),
**im lặng** (haptic rung khi có phần cứng — OPSEC: không lộ vị trí),
và **câu chữ** (template 0ms; SLM optional — màn C2) — chạy thời gian thực trên laptop cá nhân,
liên kết UAV qua **mạng riêng WiFi/4G + VPN** (không phụ thuộc hạ tầng dân dụng).

## 2. Definition of done

| Cột mốc | Nội dung | Trạng thái |
|---------|----------|------------|
| **Core (cam kết)** | **Phase 5** — tracking + mạng riêng VPN + YOLO 8 class (MVRSD) + UAV patrol/FOV + demo UAV được cấp 360P+ | = done của dự án |
| **Blocked (chờ phần cứng)** | Haptic rung (chưa có module) · Phase 6: thermal Lepton + mesh đa lính + node độc lập | chỉ khi có phần cứng/tài trợ |

"Đảm bảo hoàn thành target" được enforce bằng **acceptance criteria §5** —
mỗi mục scope có 1 lệnh kiểm thử và ngưỡng pass cụ thể. Không demo là pass khi
chưa chạy được đủ AC1–AC11 (AC4 = chế độ fallback hình ảnh cho tới khi có haptic).

## 3. Scope IN (Phase 5 — core)

| # | Mục | Chi tiết | AC |
|---|-----|----------|----|
| S1 | **Tracking (ByteTrack)** | Real-time; track_id ổn định; tính **vận tốc + tốc độ tiếp cận**; gater chuyển key từ `(target, bearing)` sang `track_id`; **nhiều target → cảnh báo target gần nhất** (câu cảnh báo + HUD có khoảng cách m + hướng từ lính); **khoảng cách target→lính**: W2 **object-height anchor** (scale = kích thước thật class / chiều cao box, ±15–25%, không cần alt UAV) → W7 **tam giác phân GPS** (GPS UAV + alt + góc chúi + FOV + pixel → lat/lon target → 2D tới lính, ±10–15%) — model pixel-scale cố định 0.05 chỉ đúng ở độ cao ~15–22m (sai ×1.5–3 ở 30–50m) | AC1–AC3 |
| S2 | **Kênh cảnh báo im lặng** | **Hiện tại: HUD flash + SLM (chưa có module rung).** Haptic (Arduino + motor) giữ làm mục blocked — bật lại khi có phần cứng, AC4 fallback = flash hình <100ms | AC4 |
| S3 | **Mạng riêng WiFi/4G + VPN (WireGuard)** | **Thay LoRa** (quyết định 2026-10-15). UDP transport giữ nguyên, thêm lớp VPN; **interface `TelemetryFeed` không đổi**; link đứt → chế độ cục bộ TTL 5s (đã có `STALE_AFTER_S`) | AC5 |
| S4 | **UAV tuần tra + FOV + theo dõi** | Flycam bay theo lộ trình quanh vị trí người được bảo vệ (MAVLink qua DJI Virtual Port của Mini 2 SE nếu verify OK, nếu không = bay tay theo route gợi ý); laptop vẽ **vùng phủ camera** (cone) lên minimap; **chế độ follow: UAV bay theo vị trí mục tiêu** (sim: theo track; real: MAVLink GOTO / HUD chỉ hướng cho phi công); **indicator target trong/ngoài tầm nhìn UAV**; mode sim khi chưa bay thật | AC6 |
| S5 | **YOLO 8 class (góc UAV)** | 8 class (chốt 2026-10-15): `person, soldier, car, motorcycle, truck, bus, boat, military_vehicle` — **gộp tất cả xe quân sự thành 1 class** (không phân tank/IFV/pháo), **loại máy bay**, **phân biệt người thường/lính**. Dataset **đặc thù UAV** (yêu cầu giảng viên 2026-10-16): MVRSD (góc drone/satellite, gộp label) + **VisDrone** (ảnh drone: person + 4 xe) + footage UAV thật tự quay (khi UAV về — gold standard, đồng thời là nguồn `soldier` B9); **tham số thu (độ cao, tốc độ, FOV) ghi vào báo cáo**; server multi-GPU; **pin version ultralytics server=laptop** | AC7 |
| S6 | **Demo UAV (i1 Pro / Mini 2 SE, 360P+)** | Video source abstraction (webcam / RTSP / UVC / file / **scrcp phone**); hiệu chỉnh YOLO cho input 360P; chạy demo end-to-end bằng UAV thật | AC8 |
| S7 | **Kênh câu chữ (template + SLM optional)** | template f-string = **chính** (0ms, 0 VRAM, luôn hoạt động); SLM qwen2.5:3b Ollama = optional qua `--slm` (cảnh báo tiếng Việt ≤12 từ, advisory chỉ cho C2) — **không** vào vòng lặp thời gian thực | AC10 |

**Dataset 8 class — trả lời "bao nhiêu đối tượng, cụ thể gì" (yêu cầu giảng viên 2026-10-16):**

| Class | Nguồn chính | Góc quay | Ghi chú |
|-------|------------|----------|---------|
| `military_vehicle` | MVRSD (~3000 ảnh, gộp mọi label xe QS) | Drone/satellite | Verify độ cao thu từ dataset card (W3) |
| `person, car, motorcycle, truck, bus` | **VisDrone** (drone) + COCO subset (chống regression) | Drone (VisDrone) | Đáp ứng "dataset thu từ UAV" |
| `soldier` | **B9: dataset mở góc UAV — Mendeley ~8k (bird's-eye, YOLO format) + Roboflow ~4.8k** (user tìm 26/10); footage UAV thật tự quay (i1 Pro) = bonus domain-adapt | Drone/bird's-eye | **Verify W3d3** (license + spot-check 50–100 label + tham số thu: độ cao/FOV/resolution); mapping Soldier→soldier, Tank→military_vehicle, People→person, Drone→loại; không có → escalate (7 class) |
| `boat` | COCO (giữ, ít fine-tune) | Đường phố | Ít gặp ở kịch bản UAV |

**Tham số thu UAV** (ghi trong báo cáo đồ án): độ cao 30–50m, tốc độ 3–5 m/s, camera hướng
xuống/tilt trước, target cách 10–50m ≈ 20–60 px.

## 4. Scope OUT (đoạn rõ để tránh phình)

- **LoRa** — thay bằng WiFi/4G + VPN (quyết định 2026-10-15).
- **E88 Pro** — không có ngân sách; dùng **UAV được cấp** thay thế.
- **Haptic module** — blocked (chưa có phần cứng); cảnh báo im lặng hiện tại = flash hình + câu chữ.
- Mesh đa lính / node RPi–Jetson / NPU trên UAV — **Tier C** (kiến trúc mesh-ready: model `Track`, `TelemetryFeed` là điểm hội tụ).
- Triển khai thật: anti-jam, rugged, mật mã đầy đủ, nguồn điện >2h.
- **Thermal ban đêm** — Phase 6, không tính trong done.
- Khoảng cách **đo** thật (stereo/ToF/LiDAR) — W2: object-height anchor (±15–25%); từ W7: **tam giác phân GPS từ UAV** (±10–15%); stereo/ToF = Phase 6.
- CQB <10m, nhóm mục tiêu di chuyển rất nhanh — YOLO không hứa.
- Target 0,2s cho SLM — **không đạt được** (floor ~0,4s qua Ollama API, đã đo).

## 5. Acceptance criteria (đo được — cơ chế "đảm bảo")

| # | Tiêu chí | Cách verify | Ngưỡng pass |
|---|----------|-------------|-------------|
| AC1 | Track ID ổn định | `test_tracking.py` (mới) trên video sim: 1 người di chuyển liên tục | ≥100 khung, re-ID <5% |
| AC2 | Tốc độ tiếp cận | Cùng script, so vel tính được với ground truth sim (W2: scale object-height anchor; W7: re-verify trên sim UAV bay vòng + tam giác phân GPS) | Sai <10% |
| AC3 | Gater theo track_id + target gần nhất | `test_telemetry_chain.py` (update): mục tiêu cắt ngưỡng 100m một lần; payload 3 target → chọn gần nhất | Báo đúng 1 lần, không lặp; câu cảnh báo có **khoảng cách + hướng** của target gần nhất |
| AC4 | Cảnh báo im lặng | **Fallback:** gater trigger → HUD flash; (haptic khi có phần cứng: decide→rung <200ms) | Flash <100ms, **không phát âm** |
| AC5 | Mạng riêng VPN | Bench 2 node qua WiFi + WireGuard: HUD nhận position 1Hz; cắt link mô phỏng đứt | Bench: sai <1m so sim; đứt link → local mode sau ≤5s, không crash |
| AC6 | UAV patrol + FOV + follow | `--sim` với lộ trình waypoints + mục tiêu di động (bay thật ở M4) | Cone FOV đúng hướng; **UAV sim bay theo vị trí mục tiêu (follow mode)**; indicator trong/ngoài tầm nhìn đúng |
| AC7 | YOLO 8 class (góc UAV) | `yolo val` trên val (MVRSD + VisDrone + soldier) + 1 clip demo có lính + xe quân sự | mAP50 ≥ 0,75; soldier + military_vehicle được box + SLM cảnh báo; **mAP 6 class COCO không giảm >5%**; weight chạy trên 3050 (cùng version ultralytics); **tham số thu (độ cao/tốc độ/FOV) ghi trong báo cáo** |
| AC8 | UAV demo live | Video 360P+ từ UAV (i1 Pro / Mini 2 SE) → HUD | ≥15fps; người trong khung → cảnh báo <2s |
| AC9 | VRAM 4GB | `nvidia-smi -l 1` 30s đầu chạy full; cố tình OOM | <3,8GB ổn định; `--cpu` khởi động lại bình thường |
| AC10 | Câu cảnh báo | Log `--sim` | template: 0ms, luôn hoạt động (không phụ thuộc Ollama); SLM optional: <1,5s/call (warm), câu ≤12 từ, tiếng Việt |
| AC11 | Demo end-to-end | Kịch bản demo 10 phút (§7) chạy một lượt | Không interrupt; đủ kênh cảnh báo |

## 6. Non-functional requirements

| Yêu cầu | Giá trị |
|---------|---------|
| Chạy trên TUF F15 (RTX 3050 4GB) | Bắt buộc; server 4× 5000 Ada chỉ để dev/fine-tune |
| Windows 11 | Guide + code target (COMx cho USB TTL) |
| Ollama native port 11434 | **Không** cần `OLLAMA_HOST` trên laptop |
| YOLO fps | 20–40 GPU (720p) / 15+ (360P) / 8–15 CPU (`--cpu`) |
| SLM latency (chỉ khi `--slm`) | 0,8–1,5s/call — chấp nhận vì gater bắn cách quãng; template = 0ms |
| Nguồn điện | 30–60 phút pin laptop |
| Degradation | 3 chế độ: đầy đủ / chỉ mạng vị trí / cục bộ — hệ không crash khi link đứt |

## 7. Kịch bản demo 10 phút (AC11)

1. Bật HUD (câu cảnh báo = template mặc định; thêm `--slm` + bật Ollama nếu muốn câu SLM — warmup tự chạy).
2. UAV bay (thật hoặc replay 360P) **theo route quanh vị trí người được bảo vệ** (GPS lính 1Hz là tâm minimap): người "địch" đi vào từ xa.
3. HUD: box đỏ + mũi tên hướng + track id ổn định + cone FOV UAV + **badge "mục tiêu trong tầm nhìn"**.
4. ~100m (ngưỡng cảnh báo): HUD flash + câu SLM trên màn C2:
   **"CẢNH BÁO: Kẻ địch cách 95m hướng Đông"** — nhiều target thì SLM **chọn target gần nhất**.
5. **UAV chuyển chế độ follow: bay theo vị trí mục tiêu** — HUD cập nhật liên tục
   khoảng cách (m) + hướng từ lính đến địch (tam giác phân GPS từ UAV, ±10–15%;
   vị trí lính từ GPS 1Hz).
6. Lính đồng đội (GPS giả) hiện chấm xanh trên minimap, không bị cảnh báo.
7. Rút link mạng riêng (tắt VPN/WiFi UAV) → HUD chuyển local mode sau 5s, không crash.
8. (Bay thật) UAV đổi waypoint / GOTO mục tiêu, FOV di chuyển theo.

## 8. Ngân sách & mốc thời gian (3 tháng = 12 tuần)

**Ngân sách: 0 VND mua mới** — dùng laptop + server dev + UAV được cấp.
(Các hạng mục 2026-10-07 cũ — LoRa, E88 Pro, module rung — đã loại/blocked.)

**Mốc (plan chi tiết từng tuần: `plans/261015-1637-phase5-3-month-roadmap/`):**
- M1 (tuần 1–2) tracking + gater track_id → AC1–AC3
- M2 (tuần 3–4) fine-tune MVRSD + VisDrone (góc UAV) trên server → AC7
- M3 (tuần 5–6) mạng riêng VPN + tích hợp camera 360P UAV → AC5, AC8 (nửa)
- M4 (tuần 7–8) FOV/patrol + tích hợp full + degradation modes → AC6, AC8
- M5 (tuần 9–12) field test + demo E2E + tài liệu đồ án + buffer → AC9–AC11

## 9. Rủi ro chính

| Rủi ro | Mitigation |
|--------|------------|
| **FOV/alt thực + DJI Virtual Port của Mini 2 SE chưa verify** (input tam giác phân GPS + tuần tra) — *downlink đã rõ 23/10: WiFi → app phone → scrcp* | i1 Pro bay thử ngay (chim tập + test scrcp); Mini 2 SE: verify khi về tay (trước W9); W1–W6 build sim-first |
| Chất lượng detection trên 360P (người 20m chỉ ~40–60 px) | Chạy model hiện tại trên frame 360P mẫu ở tuần 1; hiệu chỉnh input size/NMS ở M3 |
| MVRSD tải qua Baidu — server có thể không truy cập | Verify tuần 3; fallback: AMAD/InvictusRex (GitHub release) |
| Fine-tune 8 class degrade 6 class COCO cũ | Fine-tune trộn MVRSD + COCO; AC7 yêu cầu mAP COCO không giảm >5% |
| VPN trên thiết bị UAV node chưa rõ chạy được gì | WireGuard có build ESP32 (esp_wireguard) và Linux; chọn theo thiết bị thực tế ở M3 |
| UAV không hỗ trợ MAVLink/GCS | S4 fallback: bay tay theo route gợi ý trên map + FOV + HUD chỉ hướng cho follow — vẫn đạt AC6 (sim + bay thật) |
| VisDrone license / tham số thu chưa verify | Verify license + độ cao thu ở W3; fallback: MVRSD + COCO + footage tự quay (ghi trade-off trong báo cáo) |
| **alt/FOV của UAV được cấp chưa biết** (input tam giác phân GPS) | B1: đo khi UAV về (bay 30m, marker 10m, đếm pixel) + verify alt; sim nominal h=30m, FOV 60° tới đó; re-verify trước W9 |
| Object-height anchor: người ngồi/đằng người (box ngắn) → over-estimate | `box_h < 8px` → fallback scale 0.05; bảng kích thước theo class; W7 GPS là model chính, anchor là cầu nối + fallback |

## 10. Câu hỏi mở (chưa giải quyết)

1. **Downlink video** — ĐÃ RÕ (23/10): i1 Pro + Mini 2 SE đều **WiFi → app phone** → bridge **scrcp USB → laptop** (chốt M3).
2. **DJI Virtual Port** (Mini 2 SE) có GOTO/waypoint ổn định không (tuần tra tự động)? → verify khi nhận máy; fallback bay tay theo route gợi ý.
3. Có sẵn **SIM 4G/data** nào không (nếu không → chỉ dùng WiFi riêng)?
4. Module rung (haptic) có được cấp thêm sau này không?
5. **Nguồn ảnh class `soldier`** (B9) — **đã có 2 nguồn cụ thể (user tìm 26/10): Mendeley ~8k + Roboflow ~4.8k** → verify W3d3 (license + spot-check label + tham số thu) trước train W4; footage i1 Pro tự quay = bonus domain-adapt.
6. Alt + góc gimbal — Mini 2 SE: **có áp kế + đọc góc gimbal trong app** (23/10) → input tam giác phân GPS (W7); verify số liệu thực khi nhận máy.
