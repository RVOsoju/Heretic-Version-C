# PDR — Heretic Version C: Target, Scope & Acceptance Criteria

**Dự án:** HUD chiến thuật cho lính — YOLO + SLM Ollama (tiếng Việt) + HUD + telemetry UAV
**Ngày:** 2026-10-07 · **Cập nhật:** 2026-10-15 (không tài trợ, mạng riêng WiFi/4G+VPN, UAV được cấp 360P+ — **chưa rõ ngày về**, 8 class chốt: person/soldier + 5 xe thường + military_vehicle)
**Runtime target:** Asus TUF F15 FX507 — RTX 3050 (4GB VRAM), i7-12700H, 16GB DDR4, **Windows 11**
**Kịch bản:** 1 lính + 1 UAV. Phi sát thương — chỉ phát hiện + cảnh báo, không vũ khí tự động.

> **GIẢ ĐỊNH 2026-10-15: KHÔNG CÓ TÀI TRỢ** — chỉ dùng thiết bị có sẵn:
> laptop TUF F15, server dev (4× RTX 5000 Ada — fine-tune), **UAV được cấp (camera 360P+)**.
> Mọi phần cứng mua mới (LoRa, E88 Pro, module rung, Lepton) = **BLOCKED** cho tới khi user báo phần cứng mới.

---

## 1. Target (mission statement)

Heretic C là **hệ thống cảnh báo chiến thuật demo/đồ án đạt 70–80% sát thực tế**:
từ video trinh sát (UAV 360P+/webcam), hệ thống phát hiện + theo dõi mục tiêu, phân biệt
địch/đồng đội qua GPS, và cảnh báo lính qua 3 kênh — hình (box + minimap),
**im lặng** (haptic rung khi có phần cứng — OPSEC: không lộ vị trí),
và **câu chữ SLM** (màn C2) — chạy thời gian thực trên laptop cá nhân,
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
| S1 | **Tracking (ByteTrack)** | Real-time; track_id ổn định; tính **vận tốc + tốc độ tiếp cận**; gater chuyển key từ `(target, bearing)` sang `track_id` | AC1–AC3 |
| S2 | **Kênh cảnh báo im lặng** | **Hiện tại: HUD flash + SLM (chưa có module rung).** Haptic (Arduino + motor) giữ làm mục blocked — bật lại khi có phần cứng, AC4 fallback = flash hình <100ms | AC4 |
| S3 | **Mạng riêng WiFi/4G + VPN (WireGuard)** | **Thay LoRa** (quyết định 2026-10-15). UDP transport giữ nguyên, thêm lớp VPN; **interface `TelemetryFeed` không đổi**; link đứt → chế độ cục bộ TTL 5s (đã có `STALE_AFTER_S`) | AC5 |
| S4 | **UAV tuần tra + FOV** | Flycam bay theo lộ trình (MAVLink nếu UAV hỗ trợ, nếu không = bay tay theo route gợi ý); laptop vẽ **vùng phủ camera** (cone) lên minimap; mode sim khi chưa bay thật | AC6 |
| S5 | **YOLO 8 class** | 8 class (chốt 2026-10-15): `person, soldier, car, motorcycle, truck, bus, boat, military_vehicle` — **gộp tất cả xe quân sự thành 1 class** (không phân tank/IFV/pháo), **loại máy bay**, **phân biệt người thường/lính**. Fine-tune trên MVRSD (gộp label) + nguồn ảnh soldier (B9 — research W3); server multi-GPU; **pin version ultralytics server=laptop** | AC7 |
| S6 | **Demo UAV được cấp (camera 360P+)** | Video source abstraction (webcam / RTSP / UVC / file); hiệu chỉnh YOLO cho input 360P; chạy demo end-to-end bằng UAV thật | AC8 |
| S7 | **Kênh SLM (giữ nguyên)** | qwen2.5:3b Ollama, cảnh báo tiếng Việt ≤12 từ, advisory chỉ cho C2 — **không** vào vòng lặp thời gian thực | AC10 |

## 4. Scope OUT (đoạn rõ để tránh phình)

- **LoRa** — thay bằng WiFi/4G + VPN (quyết định 2026-10-15).
- **E88 Pro** — không có ngân sách; dùng **UAV được cấp** thay thế.
- **Haptic module** — blocked (chưa có phần cứng); cảnh báo im lặng hiện tại = flash hình + SLM.
- Mesh đa lính / node RPi–Jetson / NPU trên UAV — **Tier C** (kiến trúc mesh-ready: model `Track`, `TelemetryFeed` là điểm hội tụ).
- Triển khai thật: anti-jam, rugged, mật mã đầy đủ, nguồn điện >2h.
- **Thermal ban đêm** — Phase 6, không tính trong done.
- Khoảng cách **đo** thật (stereo/ToF) — giữ ước tính scale pixel, công khai ±30–50%.
- CQB <10m, nhóm mục tiêu di chuyển rất nhanh — YOLO không hứa.
- Target 0,2s cho SLM — **không đạt được** (floor ~0,4s qua Ollama API, đã đo).

## 5. Acceptance criteria (đo được — cơ chế "đảm bảo")

| # | Tiêu chí | Cách verify | Ngưỡng pass |
|---|----------|-------------|-------------|
| AC1 | Track ID ổn định | `test_tracking.py` (mới) trên video sim: 1 người di chuyển liên tục | ≥100 khung, re-ID <5% |
| AC2 | Tốc độ tiếp cận | Cùng script, so vel tính được với ground truth sim | Sai <10% |
| AC3 | Gater theo track_id | `test_telemetry_chain.py` (update): mục tiêu cắt ngưỡng 100m một lần | Báo đúng 1 lần, không lặp |
| AC4 | Cảnh báo im lặng | **Fallback:** gater trigger → HUD flash; (haptic khi có phần cứng: decide→rung <200ms) | Flash <100ms, **không phát âm** |
| AC5 | Mạng riêng VPN | Bench 2 node qua WiFi + WireGuard: HUD nhận position 1Hz; cắt link mô phỏng đứt | Bench: sai <1m so sim; đứt link → local mode sau ≤5s, không crash |
| AC6 | UAV patrol + FOV | `--sim` với lộ trình waypoints (bay thật ở M4) | Cone FOV hiện đúng hướng trên minimap, di chuyển theo route |
| AC7 | YOLO 8 class | `yolo val` trên val (MVRSD + soldier) + 1 clip demo có lính + xe quân sự | mAP50 ≥ 0,75; soldier + military_vehicle được box + SLM cảnh báo; **mAP 6 class COCO không giảm >5%**; weight chạy trên 3050 (cùng version ultralytics) |
| AC8 | UAV được cấp live | Video 360P+ từ UAV → HUD | ≥15fps; người trong khung → cảnh báo <2s |
| AC9 | VRAM 4GB | `nvidia-smi -l 1` 30s đầu chạy full; cố tình OOM | <3,8GB ổn định; `--cpu` khởi động lại bình thường |
| AC10 | SLM | Log `--sim` | <1,5s/call (warm); câu ≤12 từ, tiếng Việt |
| AC11 | Demo end-to-end | Kịch bản demo 10 phút (§7) chạy một lượt | Không interrupt; đủ kênh cảnh báo |

## 6. Non-functional requirements

| Yêu cầu | Giá trị |
|---------|---------|
| Chạy trên TUF F15 (RTX 3050 4GB) | Bắt buộc; server 4× 5000 Ada chỉ để dev/fine-tune |
| Windows 11 | Guide + code target (COMx cho USB TTL) |
| Ollama native port 11434 | **Không** cần `OLLAMA_HOST` trên laptop |
| YOLO fps | 20–40 GPU (720p) / 15+ (360P) / 8–15 CPU (`--cpu`) |
| SLM latency | 0,8–1,5s/call — chấp nhận vì gater bắn cách quãng |
| Nguồn điện | 30–60 phút pin laptop |
| Degradation | 3 chế độ: đầy đủ / chỉ mạng vị trí / cục bộ — hệ không crash khi link đứt |

## 7. Kịch bản demo 10 phút (AC11)

1. Bật Ollama + HUD (warmup SLM tự chạy).
2. UAV được cấp bay (hoặc replay video 360P): người "địch" đi vào từ xa.
3. HUD: box đỏ + mũi tên hướng + track id ổn định + cone FOV UAV.
4. ~100m: cảnh báo im lặng (HUD flash) + câu SLM trên màn C2.
5. Lính đồng đội (GPS giả) hiện chấm xanh trên minimap, không bị cảnh báo.
6. Rút link mạng riêng (tắt VPN/WiFi UAV) → HUD chuyển local mode sau 5s, không crash.
7. (Bay thật) UAV đổi waypoint, FOV di chuyển theo.

## 8. Ngân sách & mốc thời gian (3 tháng = 12 tuần)

**Ngân sách: 0 VND mua mới** — dùng laptop + server dev + UAV được cấp.
(Các hạng mục 2026-10-07 cũ — LoRa, E88 Pro, module rung — đã loại/blocked.)

**Mốc (plan chi tiết từng tuần: `plans/261015-1637-phase5-3-month-roadmap/`):**
- M1 (tuần 1–2) tracking + gater track_id → AC1–AC3
- M2 (tuần 3–4) fine-tune MVRSD trên server → AC7
- M3 (tuần 5–6) mạng riêng VPN + tích hợp camera 360P UAV → AC5, AC8 (nửa)
- M4 (tuần 7–8) FOV/patrol + tích hợp full + degradation modes → AC6, AC8
- M5 (tuần 9–12) field test + demo E2E + tài liệu đồ án + buffer → AC9–AC11

## 9. Rủi ro chính

| Rủi ro | Mitigation |
|--------|------------|
| **Downlink của UAV được cấp chưa rõ** (FPV 5,8G? WiFi RTSP? USB?) — điểm mù số 1 | Verify **tuần 1** khi nhận UAV; quyết định kiến trúc mạng ở M3 phụ thuộc câu trả lời này |
| Chất lượng detection trên 360P (người 20m chỉ ~40–60 px) | Chạy model hiện tại trên frame 360P mẫu ở tuần 1; hiệu chỉnh input size/NMS ở M3 |
| MVRSD tải qua Baidu — server có thể không truy cập | Verify tuần 3; fallback: AMAD/InvictusRex (GitHub release) |
| Fine-tune 8 class degrade 6 class COCO cũ | Fine-tune trộn MVRSD + COCO; AC7 yêu cầu mAP COCO không giảm >5% |
| VPN trên thiết bị UAV node chưa rõ chạy được gì | WireGuard có build ESP32 (esp_wireguard) và Linux; chọn theo thiết bị thực tế ở M3 |
| UAV không hỗ trợ MAVLink/GCS | S4 fallback: bay tay theo route gợi ý trên map + FOV — vẫn đạt AC6 (sim + bay thật) |

## 10. Câu hỏi mở (chưa giải quyết)

1. **UAV được cấp về tay ngày nào** (chưa rõ) + downlink video là loại gì (FPV 5,8GHz / WiFi RTSP / USB)? → quyết định thiết kế M3 — verify khi nhận máy; trước đó build sim-first.
2. UAV có hỗ trợ **MAVLink/GCS** (tuần tra tự động) không?
3. Có sẵn **SIM 4G/data** nào không (nếu không → chỉ dùng WiFi riêng)?
4. Module rung (haptic) có được cấp thêm sau này không?
5. **Nguồn ảnh class `soldier`** (B9) — dataset mở hay tự ghi footage thao trường? → research W3, chốt trước train W4.
