---
phase: 1
title: "Tracking ByteTrack + gater theo track_id (M1)"
status: pending
priority: P1
effort: "2w"
dependencies: []
---

# Phase 1: Tracking ByteTrack + gater theo track_id (M1)

## Overview

W1–W2: bật ByteTrack trên yolo26n, tính vận tốc + tốc độ tiếp cận theo track, chuyển gater
từ key `(target, bearing)` sang `track_id`; **object-height anchor** (W2) — tự hiệu chuẩn
scale m/px theo chiều cao box (người = thước 1.7m) thay constant `PIXEL_TO_METER = 0.05`
(sai ×1.5–3 ở độ cao bay 30–50m); **flash HUD cảnh báo im lặng** (W2, AC4 — code hiện
chưa có flash). W1 thuần code — **UAV được cấp chưa rõ ngày về**
(quyết định 2026-10-15), test 360P bằng video tổng hợp (downscale 720p → 640×360).
Khi UAV về tay: phá 3 điểm mù (B1 downlink, B2 MAVLink, B3 GPS) + retest 360P frame thật (B6).
M1 done = AC1–AC3.

## Requirements

**Functional**
- Track ID ổn định giữa các khung (ByteTrack, `persist=True`).
- Tính vận tốc (m/s) + tốc độ tiếp cận (approach, m/s — dương = đang tới gần) cho mỗi track.
- **Object-height anchor (W2)**: scale m/px tự hiệu chuẩn mỗi khung = kích thước thật class
  / chiều cao box (px) — thay constant 0.05 (hiệu chuẩn cho ~15–22m, sai ×1.5–3 ở độ cao
  bay 30–50m). Bảng: `person/soldier 1.7, motorcycle 1.6, car 1.5, truck/bus 3.5, boat 1.5,
  military_vehicle 3.0` (m). Fallback 0.05 khi class không có trong bảng hoặc `box_h < 8px`
  (quá xa, box không đủ tin). Không cần phần cứng mới; giảm nhẹ B1 (không phụ thuộc alt UAV).
- Gater key theo `track_id`: mục tiêu cắt ngưỡng 100m một lần → cảnh báo đúng 1 lần, không lặp khi track dịch chuyển.
- **Flash HUD (AC4, W2)**: gater trigger → flash toàn màn (đỏ/trắng, ≤3 khung @30fps =
  <100ms), **không phát âm** (OPSEC). Haptic giữ blocked — bật lại khi có module rung.
- 360P (W1): chạy model hiện tại trên 10 frame 640×360 tổng hợp, log precision (B6 bước 1).
- Khi UAV về tay (chưa rõ ngày): xác định loại downlink video, hỗ trợ MAVLink/GCS, nguồn vị trí GPS (B1–B3); retest 360P frame thật (B6).

**Non-functional**
- Overhead tracking <5ms/khung (ByteTrack chạy CPU, không ăn VRAM).
- `TelemetryFeed` interface không đổi (UDP 8888, JSON `{id,lat,lon,t}`).
- `--sim` và `test_telemetry_chain.py` hiện có vẫn pass (không regression).
- Chạy được trên laptop TUF F15 (runtime target).

## Architecture

Data flow:

```
frame (720p/360P)
  → YOLO yolo26n: model.track(persist=True, tracker="bytetrack.yaml")
      → boxes: (cls, xyxy, id=track_id)
  → scale frame = CLASS_HEIGHT_M[cls] / box_h_px  (object-height anchor, W2;
      fallback PIXEL_TO_METER 0.05 nếu cls không có bảng hoặc box_h < 8px)
  → TrackStore (tactical_tracker.py): per track_id, history (t, cx_px, cy_px, dist_m) 30 khung
      → velocity_mps = Δpx/Δt × scale frame
      → approach_mps = −d(dist_m)/dt
  → tactical dict: {target, track_id, distance_m, bearing, approach_mps, box, side}
  → TacticalAlertGater: key = track_id (fallback (target, bearing) khi không có track — chế độ --sim)
  → SLM + HUD; gater trigger → flash toàn màn ≤3 khung (<100ms, không âm — AC4)
```

Khi UAV về tay (ngoài code, chưa rõ ngày — verify **trước W9**): mở hộp → đọc spec → test
10 phút → ghi kết quả B1–B3 vào register điểm mù trong `plan.md` → chọn variant video cho
Phase 3 (variant tuần tra Phase 4 build trước, không chờ).

## Related Code Files

**Create**
- `tactical_tracker.py` — `TrackStore`: giữ history per track_id, tính velocity/approach, tự xoá track mất >2s.
- `test_tracking.py` — test AC1 + AC2 trên video tổng hợp (không cần phần cứng).

**Modify**
- `heretic_phase4_hud.py` — `:204` gọi `model.track(...)` thay `model(...)`; `build_tactical_data` (`:60`) thêm `track_id`, `approach_mps`; `enemies_payload` (`:80`) truyền `track_id`; thêm flag `--model`; **object-height anchor**: bảng `CLASS_HEIGHT_M` + scale = `height / box_h_px` trong `calculate_tactical_telemetry` (`:41`, fallback 0.05).
- `tactical_slm.py` — `TacticalAlertGater._key` (`:56-57`) + dict `last_warned` (`:53`): ưu tiên `track_id`, fallback key cũ.
- `tactical_hud_renderer.py` — `render_hud` (`:129`): thêm `flash=False` → overlay toàn màn đỏ/trắng khi gater trigger (≤3 khung).
- `test_telemetry_chain.py` — thêm kịch bản AC3: mục tiêu cắt ngưỡng 100m một lần → đúng 1 cảnh báo.

**Delete** — không.

## Implementation Steps

1. **W1d1** — `heretic_phase4_hud.py:204`: thay `model(frame, stream=False, verbose=False, device=yolo_device)`
   bằng `model.track(frame, persist=True, tracker="bytetrack.yaml", stream=False, verbose=False, device=yolo_device)`.
   Verify: `results[0].boxes.id` tồn tại và ổn định khi chạy webcam 30s.
2. **W1d2** — tạo `tactical_tracker.py`: class `TrackStore` với
   `update(track_id, ts, cx_px, cy_px, dist_m)`, `velocity(track_id)`, `approach(track_id)`,
   cửa sổ 5 khung; `prune(max_age_s=2.0)`.
3. **W1d3** — `heretic_phase4_hud.py`: `build_tactical_data` đọc `box.id` từ results, thêm
   `track_id` + `approach_mps` vào dict; `enemies_payload` đưa `track_id` vào payload SLM.
4. **W1d4** — `tactical_slm.py:56-57`: `_key(threat)` → `tid = threat.get("track_id");
   return tid if tid is not None else (threat.get("target"), threat.get("bearing"))`.
   `evaluate_alert` (`:94-113`) giữ nguyên logic, chỉ key thay đổi.
5. **W1d5** — 360P step 1: tạo video test tổng hợp (downscale clip 720p có người → 640×360,
   ~10 frame, người ở ~10–30m) → chạy yolo26n, log precision vào register B6.
   *(Nếu UAV về tay trong W1: xác định thêm downlink (B1), QGroundControl (B2), GPS onboard
   (B3) — ghi kết quả vào `plan.md`.)*
6. **W2d1** — object-height anchor: bảng `CLASS_HEIGHT_M` + `calculate_tactical_telemetry`
   (`heretic_phase4_hud.py:41`): `scale = CLASS_HEIGHT_M[cls] / box_h_px` (fallback 0.05 nếu
   cls không có bảng hoặc `box_h < 8px`). **Cập nhật `make_sim_frame`** (`:108`): sinh khung
   nhất quán vật lý theo (h, FOV) — `scale = 2h·tan(FOV/2)/360`, box người = 1.7/scale px,
   vị trí = distance/scale px từ tâm (h=30m, FOV 60°) — để anchor có ground truth thật.
   Verify: frame 30m tổng hợp → distance sai <25% (trước anchor: sai ×1.5–3).
7. **W2d2** — **flash HUD (AC4)**: `tactical_hud_renderer.py:129` `render_hud` thêm
   `flash=False` → overlay toàn màn đỏ/trắng; `heretic_phase4_hud.py` set flash khi gater
   trigger, giữ ≤3 khung (30fps → <100ms), không phát âm. Verify: log timestamp trigger →
   start/end flash <100ms.
8. **W2d3–4** — tạo `test_tracking.py`: video tổng hợp numpy 150 khung 30fps, 1 người di chuyển
   thẳng tốc độ biết trước → chạy `model.track` → (a) đếm lần đổi ID / tổng khung (re-ID rate),
   (b) so `velocity` tính được với ground truth (scale height anchor). In PASS/FAIL + số đo.
9. **W2d5** — `test_telemetry_chain.py`: thêm case AC3 — payload mục tiêu đi 105m → 95m
   (cắt ngưỡng 100m một lần, giữ track_id) → assert `evaluate_alert` trả cảnh báo đúng 1 lần;
   chạy full suite: `test_tracking.py`, `test_telemetry_chain.py`, `heretic_phase4_hud.py --sim`
   (16 khung) → sign-off M1.

## Success Criteria

- [ ] `python test_tracking.py` PASS: ≥100 khung, re-ID <5% — **AC1**
- [ ] `python test_tracking.py` PASS: vận tốc tính được sai <10% so ground truth sim — **AC2**
- [ ] Object-height anchor: distance trên sim tổng hợp (độ cao 30m) sai <25% so ground truth
      (trước anchor: sai ×1.5–3 do constant 0.05) — nuôi AC2/AC3
- [ ] `python test_telemetry_chain.py` PASS: mục tiêu cắt ngưỡng 100m một lần → đúng 1 cảnh báo, không lặp — **AC3**
- [ ] Flash HUD: gater trigger → flash <100ms (≤3 khung @30fps), không phát âm — **AC4**
- [ ] `python heretic_phase4_hud.py --sim` chạy xong 16 khung, cảnh báo đúng nhịp (không regression)
- [ ] 360P step 1: precision 10 frame 640×360 tổng hợp đã log vào B6 (W1)
- [ ] Khi UAV về tay (trước W9): downlink type + MAVLink + GPS xác định, 360P frame thật retest (B1–B3, B6 đóng)
- [ ] ByteTrack overhead <5ms/khung (đo `time.perf_counter` quanh `model.track` trên 100 khung)

## Risk Assessment

| Rủi ro | Mitigation |
|--------|-----------|
| ByteTrack nhảy ID khi che khuất (re-ID >5%) | Dùng `track_buffer=30` mặc định; nếu vẫn nhảy: copy `bytetrack.yaml` về repo, hạ `match_thresh`/`track_high_thres` — không sửa config trong thư viện ultralytics |
| `boxes.id` = None ở chế độ không track (--sim) | Gater fallback key `(target, bearing)` — sim không bị đụng |
| UAV về trễ / thiếu tài liệu (đã xác nhận: chưa rõ ngày về, 2026-10-15) | W1–W4 sim-first, không phụ thuộc UAV; W5–W8 chỉ cần variant video W6 + bay thật W8/W9; B1–B3 verify khi UAV về, trước W9 (field test); buffer W12 |
| Chất lượng 360P yếu (B6) | Ghi nhận W1, tune imgsz/NMS ở W6 (Phase 3); không block M1 |
| Track ID thay đổi làm gater báo lặp | AC3 test chính xác scenario này; gater reset khi track_id mới xuất hiện trong `warn_range` |
| Object-height anchor: người ngồi/đằng người (box ngắn) → over-estimate distance | `box_h < 8px` → fallback scale 0.05; bảng kích thước theo class; log scale mỗi track để kiểm tra drift; W7 (tam giác phân GPS) là model chính, anchor là cầu nối + fallback khi UAV không gửi alt |
