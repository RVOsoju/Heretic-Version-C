# Weekly Report — W2 (26/10–01/11)

**Plan:** `plans/261015-1637-phase5-3-month-roadmap/` · **Hoàn thành W2 trong 1 ngày (26/10) → M1 DONE (AC1–AC4)**
**Kế tiếp:** W3 = 02/11–08/11 — đầu tuần đọc lại report này + `plan.md` rồi tiếp tục.

## 1. Đã làm

| # | Việc | Kết quả | Bằng chứng |
|---|------|---------|------------|
| W2d1 | **Object-height anchor** | `tactical_height_anchor.py` (37 dòng): scale = kích thước class / box_h (px), fallback 0.05 (class thiếu hoặc box_h <8px); `make_sim_frame` vật lý 30m/FOV60° (scale 0.02706 m/px, người 62px — trước: blob 130px) | frame 15m/10m tổng hợp → sai **1.2–1.3%** (ngưỡng <25%; constant 0.05 cũ sai ×1.92) |
| W2d1 | Anchor vào pipeline | `build_tactical_data` per-box `box_scale` → distance + `TrackStore.update` (không còn scale cố định toàn frame) | `heretic_phase4_hud.py` |
| W2d2 | **Flash HUD (AC4)** | `render_hud(flash=)` overlay đỏ toàn màn; gater trigger → 3 khung @30fps ≈ 100ms; không API âm thanh (OPSEC) | `sim_hud_90m_quiet.png` = frame 2/3 decay, đỏ |
| W2d3–4 | **`test_tracking.py` mới** | 150 khung 30fps, person 62px (crop bus.jpg) đi 1100→680px, YOLO26n + ByteTrack thật @imgsz=1280 | detection **150/150**, re-ID **0.0%** (AC1), approach **2.32 vs gt 2.29 m/s, sai 1.2%** (AC2) |
| W2d5 | **AC3 vào test_telemetry_chain** | 105m→95m cùng track_id = đúng 1 cảnh báo; 95m lặp = im lặng; 3 target 95/42/60m → chọn **42m** | 20/20 checks (14 cũ + 6 mới) |

## 2. Quyết định kỹ thuật (chốt W2)

| Quyết định | Lý do |
|------------|-------|
| **Anchor per-box, không per-frame** | Mỗi box một scale riêng (class/box_h) — 2 target khác class trong 1 khung không sai lệch lẫn nhau; 0.05 chỉ còn là fallback. W7 tam giác phân GPS sẽ là model chính, anchor = cầu nối + fallback khi UAV không gửi alt. |
| **Sim = 30m/FOV60° làm ground truth** | `scale = 2h·tan(FOV/2)/W` — anchor test là round-trip thật (GT từ hình học sim, đo từ box), không circular. Target >17.3m (nửa bề rộng mặt đất thấy được) clamp biên khung — kích thước box vẫn đúng, vị trí chỉ đúng trong khung (domain của W7 GPS). |
| **Flash = 3 khung @30fps ≈ 100ms** | ≤3 khung theo plan; red overlay 45% blend — thấy rõ, không loá; sim loop 10 steps/s nên 3 PNG ≈ 300ms sim-time (cosmetic, live loop mới là @30fps). |
| **imgsz=1280 cho test tracking** | Khung sim 1280×720 native (PDR: 720p GPU); person 62px mất khi downscale 640 (0 box @640, conf 0.60 @1280). Live loop vẫn imgsz default — tune ở W6 theo plan. |
| **AC2 đo trên toàn track (local `detections`), không cửa sổ 5 khung** | Cửa sổ 5 khung (0.13s) jitter ±0.8 m/s — che mất sai số system; toàn track 5s loại nhiễu, còn đúng sai số scale/geometry (1.2%). |

## 3. Kiểm thử & review

- `test_telemetry_chain.py`: **20/20 PASS** (AC3 + AC4 mới)
- `test_tracking.py`: **7/7 PASS** (W2d1 anchor ×4 + AC1 ×2 + AC2)
- `--sim`: **16/16 khung**, gater nhịp 95/85/75/…/1m đúng, flash visible
- code-reviewer: **5/5 PASS, 0 BLOCKER/MAJOR**; 3 MINOR fixed ngay (full_track_approach đọc cục bộ; bỏ check tautological; strip tham chiếu plan khỏi comment code)
- 1 pre-existing note (không fix, W1-accepted): `evaluate_alert` chỉ ghi `last_warned` target gần nhất — 3 target mới đồng thời → target khác báo lại frame sau, tự ổn định sau N frame

## 4. Files chờ commit (1 commit, user tự push)

- Create: `tactical_height_anchor.py`, `test_tracking.py`
- Modify: `heretic_phase4_hud.py`, `tactical_hud_renderer.py`, `test_telemetry_chain.py`
- Docs/plans: `plan.md` (W2 ✓, Session 9), `phase-01-*.md` (completed), report này + code-review report

## 5. Unresolved

1. **Mini 2 SE** — user mua, cần về trước W9 (field test); i1 Pro = chim tập + test scrcp bridge.
2. Live webcam chưa verify (dev server không có webcam) — verify trên laptop TUF F15 (W6).
3. B4 (kiểm kho ESP32+NEO-6M) — việc user, không block code (đường sim đã chạy).
4. W4 gate chưa chốt vào plan: "nếu mAP50 <0.75 → 26s + bench VRAM laptop; 26l loại" — chờ user confirm ghi vào W4.

## 6. W3 kế hoạch (02/11–08/11) — M2: dataset

| Ngày | Việc | Verify |
|------|------|--------|
| W3d1 | **MVRSD**: test truy cập Baidu trên server (B5); fallback AMAD/InvictusRex (GitHub release) | 3000 ảnh tải về server |
| W3d2 | **VisDrone**: download subset (person + 4 xe), verify license + tham số thu (độ cao/tốc độ/FOV) từ dataset card | subset 5 class sẵn map |
| W3d3 | **Research nguồn `soldier`** (B9 — ưu tiên footage UAV tự quay); map label 8 class | B9 có kết quả (chốt trước train W4) |
| W3d4–5 | Prep data: `mvrsd-8c.yaml` (gộp label xe QS), trộn + COCO subset chống regression | yaml hợp lệ, paths resolve |

→ Xong W3 = sẵn sàng train W4 (yolo26n → 8 class, AC7: mAP50 ≥0.75, COCO giảm ≤5 điểm).
