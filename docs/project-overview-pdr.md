# PDR — Heretic Version C: Target, Scope & Acceptance Criteria

**Dự án:** HUD chiến thuật cho lính — YOLO + SLM Ollama (tiếng Việt) + HUD + telemetry UAV
**Ngày:** 2026-10-07
**Runtime target:** Asus TUF F15 FX507 — RTX 3050 (4GB VRAM), i7-12700H, 16GB DDR4, **Windows 11**
**Kịch bản:** 1 lính + 1 UAV. Phi sát thương — chỉ phát hiện + cảnh báo, không vũ khí tự động.

---

## 1. Target (mission statement)

Heretic C là **hệ thống cảnh báo chiến thuật demo/đồ án đạt 70–80% sát thực tế**:
từ video trinh sát (flycam/webcam), hệ thống phát hiện + theo dõi mục tiêu, phân biệt
địch/đồng đội qua GPS, và cảnh báo lính qua **3 kênh** — hình (box + minimap),
**im lặng** (haptic rung — OPSEC: không lộ vị trí, không phụ thuộc tai nghe),
và **câu chữ SLM** (màn C2) — chạy thời gian thực trên laptop
cá nhân 4GB VRAM, liên kết qua **LoRa riêng** (không phụ thuộc WiFi dân dụng).

## 2. Definition of done

| Cột mốc | Nội dung | Trạng thái |
|---------|----------|------------|
| **Core (cam kết)** | **Phase 5** — tracking + TTS + LoRa + UAV patrol + YOLO 8 class (thêm tank/armored) + demo E88 Pro | = done của dự án |
| **Stretch (điều kiện)** | **Phase 6** — thermal Lepton 5 (ban đêm) + mesh đa lính + nguồn điện field | chỉ khi tài trợ 5–8M được duyệt |

"Đảm bảo hoàn thành target" được enforced bằng **acceptance criteria §5** —
mỗi mục scope có 1 lệnh kiểm thử và ngưỡng pass cụ thể. Không demo là pass khi
chưa chạy được đủ AC1–AC11.

## 3. Scope IN (Phase 5 — core)

| # | Mục | Chi tiết | AC |
|---|-----|----------|----|
| S1 | **Tracking (ByteTrack)** | Real-time CPU; track_id ổn định; tính **vận tốc + tốc độ tiếp cận**; gater chuyển key từ `(target, bearing)` sang `track_id` | AC1–AC3 |
| S2 | **Haptic (rung im lặng)** | Rung khi gater cho — OPSEC: không phát âm (không lộ vị trí), không cần tai nghe; Arduino Nano + motor rung qua USB serial (tái dụng pattern `pyserial` đang có cho GPS); cảnh báo = 1–2 nhịp rung, LED nhấp nháy (tuỳ chọn) | AC4 |
| S3 | **Link LoRa 915MHz** | Transport UDP→LoRa 1Hz cho position/track; **interface `TelemetryFeed` giữ nguyên** (HUD/SLM không đổi); link đứt → chế độ cục bộ TTL 5s (đã có `STALE_AFTER_S`) | AC5 |
| S4 | **UAV tuần tra + FOV** | Flycam bay theo waypoints; laptop vẽ **vùng phủ camera** (cone) lên minimap; mode sim khi chưa có UAV | AC6 |
| S5 | **YOLO 8 class** | Fine-tune YOLO26n trên **MVRSD** (3,000 ảnh, server GPU) thêm class xe quân sự (tank/armored — danh sách class chính xác lấy từ dataset card khi chạy); **giữ 6 class COCO cũ**; thêm class mới vào `DANGEROUS_TARGETS` + prompt SLM | AC7 |
| S6 | **Demo E88 Pro** | Flycam E88 Pro (FPV 5,8GHz) + receiver phía laptop → video vào HUD (source abstraction: webcam / capture dongle / file); chạy demo end-to-end bằng flycam thật | AC8 |
| S7 | **Kênh SLM (giữ nguyên)** | qwen2.5:3b Ollama, cảnh báo tiếng Việt ≤12 từ, advisory chỉ cho C2 — **không** vào vòng lặp thời gian thực | AC10 |

## 4. Scope OUT (đoạn rõ để tránh phình)

- Mesh đa lính / node RPi–Jetson / NPU trên UAV — **Tier C, ngoài dự án này**
  (kiến trúc vẫn mesh-ready: `Track` model thống nhất, `TelemetryFeed` là điểm hội tụ).
- Triển khai thật: anti-jam, rugged, mật mã, nguồn điện >2h.
- **Thermal ban đêm** — Phase 6 stretch, không tính trong done.
- **Cảnh báo giọng nói (TTS)** — loại khỏi scope vì OPSEC (âm thanh lộ vị trí, phụ thuộc tai nghe); thay bằng haptic rung (S2).
- Khoảng cách **đo** thật (stereo/ToF) — giữ ước tính scale pixel, công khai ±30–50%.
- CQB <10m, nhóm mục tiêu di chuyển rất nhanh — COCO/YOLO không hứa.
- Target 0,2s cho SLM — **không đạt được** (floor ~0,4s qua Ollama API, đã đo).

## 5. Acceptance criteria (đo được — cơ chế "đảm bảo")

| # | Tiêu chí | Cách verify | Ngưỡng pass |
|---|----------|-------------|-------------|
| AC1 | Track ID ổn định | `test_tracking.py` (mới) trên video sim: 1 người di chuyển liên tục | ≥100 khung, re-ID <5% |
| AC2 | Tốc độ tiếp cận | Cùng script, so vel tính được với ground truth sim | Sai <10% |
| AC3 | Gater theo track_id | `test_telemetry_chain.py` (update): mục tiêu cắt ngưỡng 100m một lần | Báo đúng 1 lần, không lặp |
| AC4 | Haptic | Manual: cho gater trigger, đo từ decide → motor rung | <200ms, **không phát ra âm thanh** |
| AC5 | LoRa | Bench 2 node (gắn module thật): HUD nhận position 1Hz; rút anten mô phỏng đứt link | Bench: sai <1m so sim / field: <5m; đứt link → local mode sau ≤5s, không crash |
| AC6 | UAV patrol + FOV | `--sim` với lộ trình waypoints | Flycam di chuyển theo route, cone FOV hiện đúng hướng trên minimap |
| AC7 | YOLO 8 class | `yolo val` trên val split của MVRSD + 1 clip demo có tank | mAP50 ≥ 0,75; tank được box + SLM cảnh báo |
| AC8 | E88 Pro live | Flycam thật + receiver, chạy HUD | Video ≥20fps; người trong khung → cảnh báo <2s |
| AC9 | VRAM 4GB | `nvidia-smi -l 1` trong 30s đầu chạy full; cố tình OOM | <3,8GB ổn định; `--cpu` khởi động lại bình thường |
| AC10 | SLM | Log `--sim` | <1,5s/call (warm); câu ≤12 từ, tiếng Việt |
| AC11 | Demo end-to-end | Kịch bản demo 10 phút (§7) chạy một lượt | Không interrupt; đủ 3 kênh cảnh báo |

## 6. Non-functional requirements

| Yêu cầu | Giá trị |
|---------|---------|
| Chạy trên TUF F15 (RTX 3050 4GB) | Bắt buộc; server 4× 5000 Ada chỉ để dev/fine-tune |
| Windows 11 | Guide + code target (COMx cho USB TTL) |
| Ollama native port 11434 | **Không** cần `OLLAMA_HOST` trên laptop |
| YOLO fps | 20–40 GPU / 8–15 CPU (`--cpu`) |
| SLM latency | 0,8–1,5s/call — chấp nhận vì gater bắn cách quãng |
| Nguồn điện | 30–60 phút pin laptop (Phase 5); powerbank field = Phase 6 |
| Degradation | 3 chế độ: đầy đủ / chỉ LoRa / cục bộ — hệ không crash khi link đứt |

## 7. Kịch bản demo 10 phút (AC11)

1. Bật Ollama + HUD (warmup SLM tự chạy).
2. E88 Pro bay (hoặc replay video): người "địch" đi vào từ xa.
3. HUD: box đỏ + mũi tên hướng + track id ổn định + cone FOV UAV.
4. ~100m: cảnh báo im lặng (haptic rung) + câu SLM hiện trên màn C2.
5. Lính đồng đội (GPS giả) hiện chấm xanh trên minimap, không bị cảnh báo.
6. Rút link LoRa → HUD chuyển local mode sau 5s, không crash.
7. (Có UAV thật) flycam đổi waypoint, FOV di chuyển theo.

## 8. Ngân sách & mốc thời gian

| Hạng mục | Giá ước 2026 | Ghi chú |
|----------|--------------|---------|
| LoRa RFM95/M5Stack 915MHz ×3 + anten | 300–450k | S3 |
| Module rung (Arduino Nano + motor rung) | 50–150k | S2 |
| E88 Pro + receiver/capture phía laptop | 2–4M (chờ verify giá + loại receiver) | S6 — cần USB UVC capture, không phải analog-only |
| **Tổng Phase 5** | **~3–5M VND** | |
| FLIR Lepton 5 (Phase 6, nếu tài trợ) | 4–6M | ⚠️ E88 Pro + Lepton cùng lúc có thể >8M — **cần ưu tiên khi có số tiền thực** |

**Mốc (2–3 tuần cho Phase 5):**
M1 (tuần 1) tracking + TTS + gater track_id → AC1–AC4 ·
M2 (tuần 1–2) fine-tune MVRSD trên server → AC7 ·
M3 (tuần 2) LoRa transport (chờ linh kiện) → AC5 ·
M4 (tuần 2–3) patrol + E88 Pro + demo E2E → AC6, AC8, AC11.

## 9. Rủi ro chính

| Rủi ro | Mitigation |
|--------|------------|
| MVRSD tải qua Baidu pan — server có thể không truy cập được | Verify ngay tuần 1; fallback: AMAD/InvictusRex (GitHub release) |
| Fine-tune 8 class làm degrade 6 class COCO cũ (catastrophic forgetting) | Fine-tune trên MVRSD + một phần COCO; đo mAP cả 2 tập trước/sau |
| E88 Pro receiver không có USB UVC → không xài được `cv2.VideoCapture` | Verify loại receiver trước khi mua (cần USB camera capture) |
| LoRa 915MHz: tầm thực địa phụ thuộc địa hình | Bench trước, field test là AC5 — không hứa km trong PDR |
| Budget E88 Pro ăn vào trần 8M → Phase 6 không còn tiền | Quyết định ưu tiên khi có số tài trợ thực (câu hỏi mở §10) |

## 10. Câu hỏi mở (chưa giải quyết)

1. **Ưu tiên E88 Pro vs Lepton 5** khi chỉ có 1 mức tài trợ 5–8M — chọn theo thời điểm demo (E88 Pro) hay theo "độ thật" (Lepton ban đêm)?
2. Receiver E88 Pro: đã confirm là loại có **USB UVC** chưa?
3. MVRSD: list class chính xác (tank? armored? helicopter?) — verify từ dataset card ở M2; nếu không có "armored" riêng thì class gộp là "military vehicle".
4. Frequency LoRa 915MHz chấp nhận được cho demo tại VN (khác band 868 phổ biến Meshtastic)?
