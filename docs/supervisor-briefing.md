# Heretic Version C — Báo Cáo Trình Bày Cho Giảng Viên Hướng Dẫn

**Ngày:** 2026-10-12 · **Cập nhật:** 2026-10-16 (feedback giảng viên: dataset góc UAV + UAV theo dõi
mục tiêu + FOV indicator + **khoảng cách target→lính = tam giác phân GPS** — UAV bay vòng quanh
lính, không bay trên đầu — mục §3) · 2026-10-15 (quyết định: không tài trợ → dùng thiết bị có sẵn;
LoRa → mạng riêng WiFi/4G + WireGuard; haptic blocked → flash HUD; 8 class chốt mới; plan 12 tuần)
**Thời lượng dự kiến:** 10–15 phút
**Tài liệu chi tiết đi kèm:** `project-overview-pdr.md` (scope + tiêu chuẩn nghiệm thu) ·
`plans/261015-1637-phase5-3-month-roadmap/plan.md` (plan 12 tuần, register điểm mù B1–B9)

---

## 1. Dự án trong 1 đoạn

Heretic C là **hệ thống HUD chiến thuật phi sát thương** cho lính: nhận video trinh sát
từ UAV (360P+) → phát hiện + theo dõi mục tiêu (YOLO 8 class) → phân biệt địch/đồng đội
qua GPS → cảnh báo qua 3 kênh: **hình** (bounding box + minimap), **im lặng**
(FLASH HUD <100ms — OPSEC, không lộ vị trí; haptic rung khi có phần cứng),
và **câu chữ AI** (SLM tiếng Việt, cho màn chỉ huy). Chạy thời gian thực trên laptop cá nhân
(RTX 3050 4GB), liên kết UAV qua **mạng riêng WiFi/4G + WireGuard VPN**
— không phụ thuộc hạ tầng dân dụng. Kịch bản: **1 lính + 1 UAV được cấp** —
UAV bay quanh vị trí người được bảo vệ và **bay theo mục tiêu phát hiện**.

## 2. Target & scope (tóm tắt — chi tiết trong PDR)

- **Mục đích:** demo/đồ án đạt **70–80% sát thực tế chiến trường**.
- **Definition of done = Phase 5 (12 tuần):** tracking (track ID ổn định, tốc độ tiếp cận,
  cảnh báo target gần nhất) + cảnh báo im lặng (flash) + mạng riêng VPN + UAV tuần tra có
  vùng phủ + **follow target + FOV indicator** +
  YOLO 8 class chốt 2026-10-15: `person, soldier, car, motorcycle, truck, bus, boat,
  military_vehicle` — gộp mọi xe quân sự thành 1 class, loại máy bay, phân biệt
  người thường/lính (fine-tune MVRSD + VisDrone — góc UAV — trên server 4× GPU,
  pin version cho laptop).
- **Mỗi mục scope gắn 1 acceptance criteria đo được** (PDR §5, AC1–AC11) — ví dụ:
  track ID re-ID <5% trên 100 khung; flash cảnh báo <100ms không phát âm;
  mAP50 ≥0,75 trên val MVRSD; VRAM <3,8GB; demo end-to-end 10 phút không interrupt.
- **Giới hạn cứng (2026-10-15):** ngân sách 0 VND mua mới — chỉ dùng laptop TUF F15,
  server dev 4× RTX 5000 Ada, UAV được cấp (camera 360P+). Haptic/thermal/mesh đa lính
  = Phase 6, chỉ khi có phần cứng/tài trợ.

## 3. Trả lời feedback giảng viên (2026-10-16)

**Hỏi: dataset bao nhiêu đối tượng, cụ thể gì?** — **8 class**: `person` (dân thường),
`soldier` (kẻ địch), `car, motorcycle, truck, bus, boat` (xe thường),
`military_vehicle` (gộp mọi xe quân sự).

**Hỏi: dataset phải thu từ UAV — độ cao, tốc độ thế nào?**

| Class | Nguồn | Góc quay |
|-------|------|----------|
| `military_vehicle` | MVRSD ~3000 ảnh | Drone/satellite (độ cao thu ghi trong báo cáo) |
| `person, car, motorcycle, truck, bus` | **VisDrone** (dataset drone) + COCO subset | Drone |
| `soldier` | Footage UAV thật tự quay / dataset mở | **UAV thật** |

Tham số thu (ghi trong báo cáo đồ án): **độ cao 30–50m, tốc độ 3–5 m/s, camera hướng
xuống/tilt trước, target 10–50m ≈ 20–60 px**.

**Hỏi: nhiều object → cảnh báo cái nào?** — *Đã có trong code:* `closest =
min(alerting, key=distance)` ([tactical_slm.py:104](../tactical_slm.py)) + prompt
"chỉ lấy target gần nhất".

**Hỏi: ngưỡng khoảng cách → cảnh báo?** — Ngưỡng **100m**: <100m bắt đầu, mỗi giảm 10m
báo 1 lần, <10m mỗi giảm 1m (`tactical_slm.py:48`); cắt ngưỡng 1 lần → đúng 1 cảnh báo (AC3).

**Hỏi: xác định hướng — người được bảo vệ gửi vị trí liên tục?** — GPS người được bảo vệ →
**1Hz** (`TelemetryFeed` UDP 8888) → C2 tính **khoảng cách (m) + hướng** từ người được
bảo vệ đến target; câu SLM có cả hai: "CẢNH BÁO: Kẻ địch cách 95m hướng Đông".

**Hỏi: target có trong tầm nhìn UAV không?** — *Mới (W7):* badge HUD
**"MỤC TIÊU TRONG/NGOÀI TẦM NHÌN"** (test điểm trong cone FOV 90°, tầm 300m).

**Hỏi: UAV bay trên đầu đối tượng, đi cùng theo vật thể?** — *Mới (W7–W8):* **chế độ
follow** — sim: UAV bay tới vị trí ước tính target; real: MAVLink GOTO (nếu UAV hỗ trợ)
hoặc HUD chỉ hướng + khoảng cách cho phi công bay theo.
**Vòng demo = đúng yêu cầu: bay trên đầu → đi cùng theo → đo khoảng cách (m) + hướng → cảnh báo.**

**Hỏi: UAV bay vòng (không trên đầu lính) thì tính khoảng cách target→lính thế nào?** —
*Tối ưu (W7):* code hiện tại chỉ đúng khi UAV bay **thẳng trên đầu** (scale pixel phẳng);
UAV bay vòng → chuyển **tam giác phân GPS**: GPS UAV + **độ cao (alt)** + góc chúi camera
+ FOV + vị trí pixel target → **lat/lon target trên mặt đất** → khoảng cách + hướng tới
lính (cả hai có GPS). Sai số **±10–15%** (thay ±30–50% của scale pixel). Bay vòng
**tách 2 phạm vi**: tầm phát hiện (xuyến camera→target, 360P chỉ ~30–40m) với tầm đo
(GPS, không giới hạn) → ngưỡng 100m vẫn đạt: vòng bán kính 60–80m + follow mode.

## 4. Đã hoàn thành (có bằng chứng)

| Thành phần | Trạng thái | Bằng chứng |
|------------|-----------|------------|
| Pipeline YOLO26n → gater 100/10/1m → SLM → HUD | Chạy được, 6 class COCO | `heretic_phase4_hud.py`, chế độ `--sim` xuất 16 khung ảnh |
| SLM qwen2.5:3b (Ollama) cảnh báo tiếng Việt ≤12 từ | Latency đã đo: floor ~0,4s (server), ước 0,8–1,5s (laptop) | `tactical_slm.py --demo` |
| HUD quân dụng: bbox + minimap + địch/đồng đội theo GPS (bán kính 8m) | Hoàn thành | `tactical_hud_renderer.py` |
| Chuỗi telemetry UAV: GPS → UDP 1Hz → HUD | **11/11 kiểm thử PASS** (kèm ảnh minh chứng) | `test_telemetry_chain.py` |
| Tối ưu cho laptop 4GB VRAM (chạy thật, không phải server) | Dual-mode GPU/CPU (`--cpu`), warmup SLM, guide cài đặt Windows 11 | `laptop-deployment-guide.md` |

**Điểm trung thực (không che):** khoảng cách hiện là ước tính scale pixel (±30–50%) — từ W7
sang tam giác phân GPS (±10–15%),
chưa có track ID, chưa hoạt động ban đêm, link đang UDP/WiFi (chưa có VPN),
cảnh báo im lặng chưa có module rung — đây chính là các mục Phase 5.

## 5. Kiến trúc (5 nguyên tắc — chi tiết trong báo cáo kiến trúc)

1. **Quyết định ở edge** — node lính tự quyết "tôi bị đe dọa" cục bộ, không chờ trạm chỉ huy.
2. **Trạm chỉ huy (laptop) là optional** — mất nó, lính vẫn có cảm biến + cảnh báo cục bộ.
3. **Mọi link đều có thể đứt** — 3 chế độ: đầy đủ / suy giảm (chỉ vị trí) / cục bộ;
   dữ liệu cũ >5s bị vô hiệu (cơ chế `STALE_AFTER_S` đã có trong code).
4. **Mô hình dữ liệu thống nhất: Track** `{id, pos, vel, class, side, confidence, ttl}`
   → thay transport UDP → VPN không đụng giao diện `TelemetryFeed` (1 dòng không đổi).
5. **AI text chỉ advisory** — SLM (0,4–1,5s) cho màn chỉ huy, **không** nằm trong vòng lặp <100ms.

Lưu lượng hệ thống rất nhỏ (~30 byte/s/node) → mạng riêng WiFi/4G + WireGuard **đủ**,
không cần hạ tầng riêng.

## 6. Kế hoạch & ngân sách (Phase 5 — 12 tuần, chi tiết trong `plans/`)

| Mốc | Tuần | Nội dung |
|-----|------|----------|
| M1 | W1–W2 | Tracking ByteTrack + gater theo track_id (AC1–AC3) |
| M2 | W3–W4 | Fine-tune YOLO 8 class MVRSD, multi-GPU, pin version (AC7) — song song M1 |
| M3 | W5–W6 | Mạng riêng WiFi/4G + WireGuard (bench 2 node) + camera 360P (AC5, nửa AC8) |
| M4 | W7–W8 | Cone FOV + **follow target** + FOV indicator + tuần tra + tích hợp full 3 chế độ degradation (AC6, AC8) |
| M5 | W9–W12 | Field test + stress + demo E2E 10 phút + tài liệu (AC9–AC11, W12 buffer) |

**Ngân sách: 0 VND mua mới** — dùng laptop TUF F15 + server dev 4× RTX 5000 Ada +
UAV được cấp. Phần cứng mới (haptic, ESP32 node, thermal) chỉ khi được cấp/tài trợ.

**Register điểm mù (B1–B9)** — mọi điểm mù có deadline giải quyết (plan.md):
UAV chưa rõ ngày về (B1–B3 → verify khi UAV về, trước W9); nguồn ảnh class `soldier` (B9 → W3d3);
truy cập Baidu (B5 → W3d1); 360P chất lượng (B6 → W1 bước 1, retest khi UAV về)…

## 7. Rủi ro chính

| Rủi ro | Mitigation |
|--------|------------|
| **Downlink của UAV được cấp chưa rõ** (FPV 5.8G? WiFi RTSP? USB?) — điểm mù số 1 | Verify khi nhận UAV (trước W9); build sim-first W1–W6; 2 variant đã thiết kế sẵn |
| Chất lượng detection trên 360P (người 20m chỉ ~40–60 px) | W1: test model hiện tại trên 360P tổng hợp; tune imgsz/NMS ở W6 |
| MVRSD tải qua Baidu — server có thể không truy cập | Verify W3d1; fallback: AMAD/InvictusRex (GitHub release) |
| Không có nguồn ảnh class `soldier` (B9) | Research W3d3; fallback: tự ghi footage thao trường; nếu không → escalate (giữ 7 class) |
| Fine-tune 8 class degrade 6 class COCO cũ | Trộn MVRSD + COCO trong 1 train; AC7: mAP COCO giảm ≤5 điểm |

## 8. Câu hỏi cần ý kiến giảng viên

1. Plan 12 tuần + register điểm mù B1–B9 (mỗi điểm mù có deadline) — đã đủ rõ để theo dõi
   tiến độ tuần này qua tuần khác chưa?
2. 8 class chốt (`person, soldier` + 5 xe thường + `military_vehicle` gộp) với dataset góc UAV
   (MVRSD drone + **VisDrone** + footage UAV tự quay, tham số thu độ cao 30–50m / 3–5 m/s
   ghi trong báo cáo) — chấp nhận, hay cần tách lại class xe quân sự / thêm nguồn dataset?
3. UAV được cấp chưa rõ ngày về — nếu UAV về sau W8, demo W11 chạy bằng **replay video 360P**
   (PDR cho phép) có chấp nhận không?
4. Module rung (haptic) có khả năng được cấp thêm trước demo không? Nếu không →
   cảnh báo im lặng = flash HUD <100ms (fallback đã chốt).

## 9. Danh mục tài liệu

| File | Nội dung |
|------|----------|
| `project-overview-pdr.md` | Target, scope IN/OUT, 11 acceptance criteria, mốc, rủi ro |
| `plans/261015-1637-phase5-3-month-roadmap/` | Plan 12 tuần (5 phase) + register điểm mù B1–B9 + validation log |
| `battlefield-realism-architecture-report.md` | Phân tích gap 8 điểm, kiến trúc edge-first, 3 tier nâng cấp |
| `hardware-bom.md` | BOM chi tiết 3 node, spec firmware ESP32 |
| `laptop-deployment-guide.md` | Cài đặt + các bước kiểm thử trên laptop TUF F15 (Windows 11) |
