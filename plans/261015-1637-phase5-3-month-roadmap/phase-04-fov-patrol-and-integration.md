---
phase: 4
title: "Cone FOV + tuần tra UAV + tích hợp full 3 chế độ (M4)"
status: pending
priority: P1
effort: "2w"
dependencies: [phase-01, phase-02, phase-03]
---

# Phase 4: Cone FOV + tuần tra UAV + tích hợp full (M4)

## Overview

W7–W8: vẽ vùng phủ camera (cone FOV) của UAV lên minimap + logic tuần tra —
**build variant B (route gợi ý bay tay) trước**, chạy được mọi trường hợp;
variant A (MAVLink upload mission) chỉ viết thêm nếu B2=yes khi UAV về tay
(chưa rõ ngày, 2026-10-15). W8: tích hợp full (tracking + model 8 class +
camera 360P + telemetry qua VPN) với 3 chế độ degradation và link-loss test.
M4 done = AC6 + AC8.

## Requirements

**Functional**
- Cone FOV: vị trí UAV (từ `TelemetryFeed`) + hướng bay → đa giác cone (FOV 90°, tầm ~300m)
  vẽ lên minimap, chuyển động theo UAV.
- Tuần tra: lộ trình waypoint (5 điểm). **Variant A** (MAVLink hỗ trợ — B2): upload mission
  tự động. **Variant B** (không hỗ trợ): route gợi ý vẽ trên minimap + danh sách console,
  phi công bay tay theo.
- 3 chế độ: **FULL** (video + vị trí) / **POS-ONLY** (mất video) / **LOCAL** (mất mọi link) —
  badge chế độ hiện trên HUD; chuyển chế độ ≤5s, không crash.
- `--sim` chạy full pipeline offline (route sim + video file).

**Non-functional**
- `TelemetryFeed` không đổi (TTL 5s là cơ chế degradation có sẵn).
- Không crash ở mọi tổ hợp link đứt/khôi phục.
- Chạy 10 phút liên tục trên laptop 4GB VRAM.

## Architecture

```
TelemetryFeed.relative_positions() (không đổi) ──► vị trí UAV (dx, dy)
hướng UAV: MAVLink (A) / 2 điểm GPS cách 5s (B) / --uav-heading (thủ công)
  → tactical_uav_fov.py: fov_cone(uav_xy, heading_deg, fov_deg=90, range_m=300) → polygon (dx, dy)
  → draw_minimap (tactical_hud_renderer.py:55) + tham số cone → fillPoly trong minimap

uav_patrol_sim.py: list waypoint (lat, lon) → interpol 5 m/s → phát UDP 8888 1Hz
  {"id":"uav","lat","lon","t"} (đúng format hardware-bom §5) → TelemetryFeed (closed loop sim)
  + vẽ đường route lên minimap

Variant A only: uav_mavlink_controller.py (pymavlink): connect radio USB →
  MISSION_ITEM_INT upload → ARM + TAKEOFF → follow waypoint

Chế độ (heretic_phase4_hud.py):
  video_ok = cap.read() sống;  pos_ok = feed.fresh("uav")
  FULL = video_ok & pos_ok;  POS-ONLY = !video_ok & pos_ok;  LOCAL = !pos_ok
  → badge text qua renderer; TTL 5s tự vô hiệu dữ liệu cũ
```

## Related Code Files

**Create**
- `tactical_uav_fov.py` — `fov_cone(...) → [(dx,dy), ...]` (toạ độ equirectangular local, cùng hệ `tactical_telemetry_feed.py:79-80`) + hàm `draw_fov_cone(frame, ox, oy, px_per_m, cone)` để renderer không phình.
- `uav_patrol_sim.py` — lộ trình waypoint, phát UDP 8888 1Hz, vẽ route.
- `uav_mavlink_controller.py` — **chỉ nếu variant A** (B2=yes); pymavlink.
- `test_degradation_modes.py` — bật full → kill video → kill telemetry → assert chuyển chế độ + không crash.

**Modify**
- `tactical_hud_renderer.py` — `draw_minimap` (`:55`) thêm tham số `uav_cone=None`; `render_hud` (`:129`) thêm `mode_text` badge.
- `heretic_phase4_hud.py` — tính heading + cone, truyền vào `render_hud`; phát hiện chế độ; flag `--uav-heading`.

**Delete** — không.

## Implementation Steps

1. **W7d1** — `tactical_uav_fov.py`: `fov_cone(uav_dx, uav_dy, heading_deg, fov_deg=90.0,
   range_m=300.0)` → 5–7 điểm đa giác (đỉnh tại UAV); `draw_fov_cone(...)` alpha-blend.
2. **W7d2** — `tactical_hud_renderer.py:55` `draw_minimap`: thêm `uav_cone=None`;
   gọi `draw_fov_cone` sau khi vẽ chấm UAV.
3. **W7d3** — `heretic_phase4_hud.py`: heading = `atan2` của 2 vị trí UAV cách 5s trong feed
   (giữ buffer nhỏ); fallback `--uav-heading`; truyền cone vào `render_hud`.
4. **W7d4** — `uav_patrol_sim.py`: 5 waypoint quanh vị trí lính (bán kính 50–80m),
   tốc độ 5 m/s, phát UDP 8888 1Hz (format `hardware-bom.md` §5); vẽ đường route
   (dashed) lên minimap.
5. **W7d5** — **variant tuần tra B build trước** (route gợi ý: route trên map + print danh
   sách waypoint console cho phi công) — chạy được mọi trường hợp, không phụ thuộc UAV.
   Nếu B2=yes (khi UAV về tay): viết thêm `uav_mavlink_controller.py`
   (pymavlink: connect `COMx`, upload MISSION, ARM, TAKEOFF, GOTO).
6. **W8d1** — `heretic_phase4_hud.py`: phát hiện chế độ FULL/POS-ONLY/LOCAL mỗi khung
   (rẻ: 2 flag boolean); badge qua `render_hud(mode_text=...)`.
7. **W8d2** — `test_degradation_modes.py`: source file + sender UDP → FULL; kết thúc file
   video → POS-ONLY; kill sender → LOCAL ≤5s; assert không crash, log chuyển chế độ.
8. **W8d3** — tích hợp full 10 phút: model 8 class (W4) + source 360P (W6) + telemetry VPN
   (W5) + FOV cone; ghi hình; kiểm tra badge + fps + không crash.
9. **W8d4** — bay thật (nếu UAV + trời cho phép): FOV theo hướng bay thật (AC6 real);
   nếu không bay được: sign-off bằng sim + bench, ghi lý do.

## Success Criteria

- [ ] `python heretic_phase4_hud.py --sim` + `uav_patrol_sim.py`: cone FOV hiện đúng hướng,
      di chuyển theo route waypoint — **AC6** (sim)
- [ ] Bay thật (nếu bay được): cone lệch hướng bay thực <45° — **AC6** (real)
- [ ] `python test_degradation_modes.py` PASS: FULL→POS-ONLY→LOCAL, mỗi chuyển ≤5s, không crash — **AC5/AC8**
- [ ] Chạy tích hợp 10 phút: ≥15fps, không crash, badge chế độ hiện — **AC8**
- [ ] `git diff tactical_telemetry_feed.py` rỗng — ràng buộc interface

## Risk Assessment

| Rủi ro | Mitigation |
|--------|-----------|
| Không có heading UAV (không MAVLink, GPS thưa/UAV đứng yên) | Heading từ 2 điểm cách 5s; UAV đứng yên → `--uav-heading` thủ công; ghi rõ giới hạn trong đồ án |
| MAVLink link không ổn định (variant A) | Fallback variant B (bay tay theo route gợi ý) — AC6 vẫn đạt qua sim + route; thời gian A chỉ là "nice to have" |
| `tactical_hud_renderer.py` vượt 200 dòng | Hàm vẽ cone tách sẵn trong `tactical_uav_fov.py`; renderer chỉ gọi |
| Chạy 10 phút OOM VRAM 4GB | YOLO `--cpu` (SLM giữ GPU) — fallback đã có từ Phase 4 cũ, stress test chính ở W10 |
| Bay thật bị thời tiết/sân bay chặn | PDR §7 cho phép "replay video 360P"; demo vẫn đạt AC11, ghi lý do không bay thật |
