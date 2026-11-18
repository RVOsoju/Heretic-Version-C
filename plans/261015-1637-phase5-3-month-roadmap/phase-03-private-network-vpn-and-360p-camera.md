---
phase: 3
title: "Mạng riêng + link loss + video scrcp + camera 360P (M3)"
status: pending
priority: P1
effort: "2w"
dependencies: [phase-01]
---

# Phase 3: Mạng riêng + link loss + video scrcp + camera 360P (M3)

## Overview

W5–W6: **re-scope 18/11 (user chốt) — bỏ bench WireGuard 2 node** (không có SIM 4G,
demo nằm trong vùng phủ 1 AP; kiến trúc trong suốt transport — thêm WG sau chỉ là
1 config). **Đường video đã chốt**: Mini 2 SE không có link trực tiếp laptop
(không RTSP, không SDK) — drone → phone (DJI Fly) → **USB scrcp** → laptop
(chốt 23/10).

W5: hotspot WPA2 riêng + UDP 8888 (`udp_position_sender.py` + `test_link_loss.py`)
+ **link-loss drill** (≤5s local, không crash) + **test pipe scrcp** (clip K2 trên
phone → laptop → capture frame — không cần UAV). W6: video source abstraction
(`--source webcam/rtsp/uvc/file/scrcp`) + hiệu chỉnh YOLO cho 360P (nửa AC8).
**Vị trí GPS drone không trích được** (không có SDK Mini 2 SE) → chấm UAV trên
minimap = mô phỏng qua UDP 8888 (limitation ghi trong báo cáo). `TelemetryFeed`
interface (UDP 8888, JSON `{id,lat,lon,t}`) **không đổi 1 dòng**.

## Requirements

**Functional**
- Mạng riêng không phụ thuộc hạ tầng dân dụng: laptop + node telemetry trên 1 AP riêng
  (hotspot Windows / router có sẵn), WPA2. **Không WireGuard** (chốt 18/11).
- `udp_position_sender.py` trên node: phát `{"id","lat","lon","t"}` 1Hz (vị trí sim
  di chuyển, biết ground truth) — thay firmware ESP32 nếu không có phần cứng (B4).
- Link đứt → `TelemetryFeed` tự chuyển local sau ≤5s (`STALE_AFTER_S`,
  `tactical_telemetry_feed.py:23`), không crash.
- **Video pipe scrcp**: phone (DJI Fly / video) → USB scrcp → laptop → Python
  capture frame được ở fps dùng được (test bằng clip K2 trên phone — không cần drone).
- `--source {webcam|rtsp|uvc|file|scrcp}` + `--source-url` cho mọi nguồn video (W6).
- 360P: ≥15fps trên RTX 3050; người trong khung → cảnh báo <2s.

**Non-functional**
- `tactical_telemetry_feed.py` không sửa (git diff rỗng) — transport trong suốt với app.
- Setup mạng ghi thành tài liệu để đưa vào đồ án (reproducible).

## Architecture

```
Drone (Mini 2 SE) ──OcuSync──► phone (DJI Fly) ──USB scrcp──► laptop:
                                            capture frame (mss) ──► cv2 frame ──► HUD
Node telemetry (phone / laptop 2 / ESP32) ──UDP 8888 (hotspot WPA2 riêng)──► laptop
GPS drone: không trích được (không SDK) → udp_position_sender mô phỏng (chấm UAV)
```

Quy tắc: **mọi thứ đổ về UDP 8888 như cũ** — `TelemetryFeed`
(`tactical_telemetry_feed.py:31-82`) không đổi. Video đi USB, không đi mạng.

## Related Code Files

**Create**
- `udp_position_sender.py` — script node: phát `{"id","lat","lon","t"}` 1Hz tới laptop
  (thay thế firmware ESP32 nếu không có phần cứng — B4; format đúng `hardware-bom.md` §5).
- `test_link_loss.py` — bench AC5: node phát UDP 1Hz → HUD nhận; sai vị trí <1m so sim;
  cắt link → stale ≤5s, không crash.
- `tactical_video_source.py` — `open_video_source(kind, url) → cv2.VideoCapture`
  (webcam index / RTSP FFMPEG buffer nhỏ / UVC path / file / **scrcp window**);
  trả fps thực đo.
- `docs/network-setup.md` — hướng dựng mạng: AP WPA2 riêng, `udp_position_sender.py`,
  lệnh verify, quy trình link-loss drill.

**Modify**
- `heretic_phase4_hud.py` — thêm flag `--source`/`--source-url`; thay khối
  `cv2.VideoCapture(0)` (`:193-195`) bằng `open_video_source`; truyền `imgsz` hợp lý
  cho 360P.

**Delete** — không.

## Implementation Steps

1. **W5d1** — dựng mạng riêng: Windows Mobile Hotspot (laptop làm AP) hoặc router có sẵn;
   WPA2; node tham gia; ping 2 chiều OK.
2. **W5d2** — `udp_position_sender.py` trên node (vị trí sim di chuyển, biết ground truth);
   `TelemetryFeed` trên laptop nhận 1Hz.
3. **W5d3** — `test_link_loss.py`: HUD nhận position 1Hz, sai <1m so sim → PASS.
4. **W5d4** — **link-loss drill**: tắt WiFi node → assert `feed.fresh("uav")`
   = None sau ≤5s, HUD không crash.
5. **W5d5** — **test scrcp**: clip K2 trên phone (không cần drone) → scrcp USB →
   laptop; capture frame bằng Python (mss/directscreen) → đo fps dùng được;
   ghi kết quả → input thiết kế `--source scrcp` cho W6.
6. **W6d1** — tạo `tactical_video_source.py`: 5 kind (webcam/rtsp/uvc/file/scrcp);
   RTSP dùng `cv2.CAP_FFMPEG` + `CAP_PROP_BUFFERSIZE=1`; in fps thực đo sau 100 khung.
7. **W6d2** — `heretic_phase4_hud.py`: thêm `--source`/`--source-url`; thay `:193-195`;
   với 360P truyền `imgsz=640` vào `model.track`.
8. **W6d3** — tune 360P: conf 0.4, imgsz 640 (native 640×360, không upscale); bench fps
   trên 3050; clip 360P có người → đo thời gian từ vào khung đến cảnh báo (<2s).
9. **W6d4** — update `docs/laptop-deployment-guide.md`: mục mạng riêng + `--source` + scrcp.

## Success Criteria

- [ ] Hotspot WPA2 riêng: laptop + node cùng AP; ping 2 chiều <20ms
- [ ] `python test_link_loss.py` PASS: HUD nhận position 1Hz qua mạng riêng, sai <1m
      so sim; cắt link → local mode ≤5s, không crash — **AC5**
- [ ] **Pipe scrcp**: clip K2 trên phone → laptop → Python capture frame fps dùng
      được — **AC8** (đường đi)
- [ ] `python heretic_phase4_hud.py --source scrcp` (hoặc `file`/`webcam`) chạy
      **≥15fps @360P** — **AC8** (nửa)
- [ ] Người trong khung 360P → cảnh báo HUD <2s (đo timestamp log) — **AC8** (nửa)
- [ ] `git diff tactical_telemetry_feed.py` rỗng — ràng buộc interface
- [ ] `docs/network-setup.md` đủ để người khác dựng lại mạng từ 0

## Risk Assessment

| Rủi ro | Mitigation |
|--------|-----------|
| Capture scrcp (window mirror) fps/latency yếu trên Windows | W5d5 đo sớm (clip K2 trên phone); fallback: app capture xuất khung trực tiếp, hoặc vòng `adb exec-out screencap` (fps thấp hơn); không đạt → PDR §7 cho phép replay video 360P qua `file` |
| RTSP lag/đứt (nếu sau này có source RTSP thật) | `rtsp_transport;tcp`, buffer size 1; chấp nhận delay 1–2s và công khai trong đồ án |
| Không có 4G SIM (B7) | WiFi-only; demo site trong vùng phủ AP — **chốt 18/11: bỏ WireGuard, không 4G** |
| 360P <15fps | đóng app nặng, tắt hardware acceleration trình duyệt; nếu vẫn chưa đủ → `imgsz=480` + ghi nhận trade-off chất lượng |
| IP laptop đổi giữa các lần demo | DHCP reservation trên AP + tài liệu `docs/network-setup.md` ghi IP tĩnh |
