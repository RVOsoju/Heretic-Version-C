---
phase: 3
title: "Mạng riêng + link loss + video AirPlay + camera 360P (M3)"
status: pending
priority: P1
effort: "2w"
dependencies: [phase-01]
---

# Phase 3: Mạng riêng + link loss + video AirPlay + camera 360P (M3)

## Overview

W5–W6: **re-scope 18/11 (user chốt) — bỏ bench WireGuard 2 node** (không có SIM 4G,
demo nằm trong vùng phủ 1 AP; kiến trúc trong suốt transport — thêm WG sau chỉ là
1 config). **Đường video đã chốt**: Mini 2 SE không có link trực tiếp laptop
(không RTSP, không SDK) — drone → iPhone (DJI Fly) → **AirPlay** → laptop
(chốt 23/10; **sửa 19/11: phone là iOS → AirPlay, không scrcp** — scrcp/adb
chỉ chạy Android).

W5: hotspot WPA2 riêng + UDP 8888 (`udp_position_sender.py` + `test_link_loss.py`)
+ **link-loss drill** (≤5s local, không crash) + **test pipe AirPlay qua WiFi**
(qua hotspot — phi công đứng xa, không cable; clip K2 trên iPhone,
không cần UAV). W6: video source abstraction
(`--source webcam/rtsp/uvc/file/window` — window = capture AirPlayReceiver
theo title) + hiệu chỉnh YOLO cho 360P (nửa AC8).
**Quyết định 19/11: WiFi-only** (loại USB/Bluetooth/scrcp — iOS) → mạng riêng giờ là
**critical path** (mang video + telemetry) → bench W5 = bench chất lượng mạng
(fps ổn định, packet loss, latency, tải đồng thời 2 dòng).
**Vị trí GPS drone không trích được** (không có SDK Mini 2 SE) → chấm UAV trên
minimap = mô phỏng qua UDP 8888 (limitation ghi trong báo cáo). `TelemetryFeed`
interface (UDP 8888, JSON `{id,lat,lon,t}`) **không đổi 1 dòng**.

**Code 19/11 ✓** (server): `udp_position_sender.py` + `test_link_loss.py` (7/7,
code-reviewed — 1 Important + 2 Minor đã fix) + `network-setup.md` (bản AirPlay + iSH)
+ `tactical_video_source.py` (5 kinds, window = mss+pywin32) + `bench_window_capture.py`
+ `--source`/`--source-url` wire vào `heretic_phase4_hud.py` (smoke: file kind OK,
pipeline chạy tới display boundary). **Còn laptop (23/11):** W5d1 hotspot + W5d5 bench
AirPlay + drill → số liệu → AC5; W6d3 tune 360P + đo ≥15fps + cảnh báo <2s → M3.

## Requirements

**Functional**
- Mạng riêng không phụ thuộc hạ tầng dân dụng: laptop + node telemetry trên 1 AP riêng
  (hotspot Windows / router có sẵn), WPA2. **Không WireGuard** (chốt 18/11).
- `udp_position_sender.py` trên node: phát `{"id","lat","lon","t"}` 1Hz (vị trí sim
  di chuyển, biết ground truth) — thay firmware ESP32 nếu không có phần cứng (B4).
- Link đứt → `TelemetryFeed` tự chuyển local sau ≤5s (`STALE_AFTER_S`,
  `tactical_telemetry_feed.py:23`), không crash.
- **Video pipe AirPlay qua WiFi**: iPhone (DJI Fly / video) → **AirPlay**
  (screen mirroring → window AirPlayReceiver trên laptop, qua hotspot) →
  Python capture frame được ở fps dùng được (test bằng clip K2 trên iPhone —
  không cần drone). Không dùng USB (iOS không có USB debugging/adb).
- `--source {webcam|rtsp|uvc|file|window}` (window = AirPlayReceiver/scrcp,
  tìm theo title) + `--source-url` cho mọi nguồn video (W6).
- 360P: ≥15fps trên RTX 3050; người trong khung → cảnh báo <2s.

**Non-functional**
- `tactical_telemetry_feed.py` không sửa (git diff rỗng) — transport trong suốt với app.
- Setup mạng ghi thành tài liệu để đưa vào đồ án (reproducible).

## Architecture

```
Drone (Mini 2 SE) ──OcuSync 5.8GHz──► iPhone (DJI Fly)
iPhone ──AirPlay (qua hotspot WPA2)──► laptop:
                                            window AirPlayReceiver → capture (mss) ──► cv2 frame ──► HUD
Node telemetry (iSH trên iPhone) ──UDP 8888 (cùng hotspot)──► laptop
GPS drone: không trích được (không SDK) → udp_position_sender mô phỏng (chấm UAV)
```

Quy tắc: **mọi thứ đổ về hotspot WPA2 riêng** — `TelemetryFeed`
(`tactical_telemetry_feed.py:31-82`) không đổi; AirPlay và UDP 8888 chạy song song
trên cùng 1 mạng. **Tách băng tần**: OcuSync ép 5.8GHz (DJI Fly), hotspot
Windows chỉ phát 2.4GHz → không tranh sóng.

## Related Code Files

**Create**
- `udp_position_sender.py` — script node: phát `{"id","lat","lon","t"}` 1Hz tới laptop
  (thay thế firmware ESP32 nếu không có phần cứng — B4; format đúng `hardware-bom.md` §5).
- `test_link_loss.py` — bench AC5: node phát UDP 1Hz → HUD nhận; sai vị trí <1m so sim;
  cắt link → stale ≤5s, không crash.
- `tactical_video_source.py` — `open_video_source(kind, url) → cv2.VideoCapture`
  (webcam index / RTSP FFMPEG buffer nhỏ / UVC path / file / **window**
  — capture window AirPlayReceiver/scrcp theo title, mss + pywin32);
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
5. **W5d5** — **test AirPlay qua WiFi (bench chất lượng mạng)**: clip K2 trên iPhone
   (không cần drone) → AirPlay → window AirPlayReceiver → laptop; capture frame bằng
   Python (mss) → đo: fps video ổn định, packet loss, latency, **chạy đồng thời
   UDP 8888** (đúng điều kiện demo); nếu có i1 Pro → bay thật thay clip (mạnh hơn).
   Ghi kết quả → input thiết kế `--source window` cho W6.
6. **W6d1** — tạo `tactical_video_source.py`: 5 kind (webcam/rtsp/uvc/file/window);
   RTSP dùng `cv2.CAP_FFMPEG` + `CAP_PROP_BUFFERSIZE=1`; in fps thực đo sau 100 khung.
7. **W6d2** — `heretic_phase4_hud.py`: thêm `--source`/`--source-url`; thay `:193-195`;
   với 360P truyền `imgsz=640` vào `model.track`.
8. **W6d3** — tune 360P: conf 0.4, imgsz 640 (native 640×360, không upscale); bench fps
   trên 3050; clip 360P có người → đo thời gian từ vào khung đến cảnh báo (<2s).
9. **W6d4** — update `docs/laptop-deployment-guide.md`: mục mạng riêng + `--source` + AirPlay.

## Success Criteria

- [ ] Hotspot WPA2 riêng: laptop + node cùng AP; ping 2 chiều <20ms
- [ ] `python test_link_loss.py` PASS: HUD nhận position 1Hz qua mạng riêng, sai <1m
      so sim; cắt link → local mode ≤5s, không crash — **AC5**
- [ ] **Pipe AirPlay qua WiFi**: clip K2 trên iPhone → AirPlay → AirPlayReceiver →
      laptop → Python capture frame fps dùng được, **đồng thời UDP 8888 không
      degrade** — **AC8** (đường đi)
- [ ] `python heretic_phase4_hud.py --source window` (hoặc `file`/`webcam`) chạy
      **≥15fps @360P** — **AC8** (nửa)
- [ ] Người trong khung 360P → cảnh báo HUD <2s (đo timestamp log) — **AC8** (nửa)
- [ ] `git diff tactical_telemetry_feed.py` rỗng — ràng buộc interface
- [ ] `docs/network-setup.md` đủ để người khác dựng lại mạng từ 0

## Risk Assessment

| Rủi ro | Mitigation |
|--------|-----------|
| **Hotspot Windows chỉ phát 2.4GHz** — tranh sóng với OcuSync 2.4GHz + AirPlay cùng 2.4GHz | Ép link drone sang **5.8GHz** trong DJI Fly; verify W5d5 (bay i1 Pro + đo chất lượng video); fallback: router có sẵn làm AP 5GHz |
| **Hotspot Windows drop client / yếu khi mang tải video** (critical path) | W5d5 đo sớm dưới tải đồng thời (video + UDP); fallback: router có sẵn làm AP; không đạt → PDR §7 cho phép replay video 360P qua `file` |
| Capture **AirPlay** (window) fps/latency yếu trên Windows 2.4GHz | W5d5 đo sớm (clip K2 trên iPhone); fallback: router có sẵn làm AP 5GHz; không đạt → replay file |
| RTSP lag/đứt (nếu sau này có source RTSP thật) | `rtsp_transport;tcp`, buffer size 1; chấp nhận delay 1–2s và công khai trong đồ án |
| Không có 4G SIM (B7) | WiFi-only; demo site trong vùng phủ AP — **chốt 18/11: bỏ WireGuard, không 4G** |
| 360P <15fps | đóng app nặng, tắt hardware acceleration trình duyệt; nếu vẫn chưa đủ → `imgsz=480` + ghi nhận trade-off chất lượng |
| IP laptop đổi giữa các lần demo | DHCP reservation trên AP + tài liệu `docs/network-setup.md` ghi IP tĩnh |
