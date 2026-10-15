---
phase: 3
title: "Mạng riêng WiFi/4G + WireGuard + camera 360P (M3)"
status: pending
priority: P1
effort: "2w"
dependencies: [phase-01]
---

# Phase 3: Mạng riêng WiFi/4G + WireGuard + camera 360P (M3)

## Overview

W5–W6: dựng mạng riêng (WiFi/4G) + WireGuard — **sim-first, không phụ thuộc UAV**
(UAV được cấp chưa rõ ngày về, 2026-10-15): W5 bench 2 node (laptop + điện thoại/laptop 2)
đạt AC5; W6: video source abstraction (`--source webcam/rtsp/uvc/file`) + hiệu chỉnh YOLO
cho 360P bằng file/webcam (nửa AC8). **Variant video A (RTSP) / B (UVC) chốt khi UAV về tay**
(verify trước W9). `TelemetryFeed` interface (UDP 8888, JSON `{id,lat,lon,t}`) **không đổi 1 dòng**.

## Requirements

**Functional**
- Mạng riêng không phụ thuộc hạ tầng dân dụng: laptop + node telemetry trên 1 AP riêng (hotspot Windows / router có sẵn), WPA2.
- WireGuard giữa laptop ⇄ node (node = điện thoại / laptop 2 / ESP32 nếu có — B4).
- `--source {webcam|rtsp|uvc|file}` + `--source-url` cho mọi nguồn video.
- 360P: ≥15fps trên RTX 3050; người trong khung → cảnh báo <2s.
- Link đứt → `TelemetryFeed` tự chuyển local sau ≤5s (`STALE_AFTER_S`, `tactical_telemetry_feed.py:23`), không crash.

**Non-functional**
- `tactical_telemetry_feed.py` không sửa (git diff rỗng) — VPN trong suốt với app.
- Setup mạng ghi thành tài liệu để đưa vào đồ án (reproducible).
- 4G SIM (B7): nếu có → node ra ngoài vùng WiFi vẫn về laptop qua 4G+WG; nếu không → WiFi-only, demo trong vùng phủ AP.

## Architecture

**2 variants (chọn khi UAV về tay, verify trước W9 — B1):**

**Variant A — UAV có camera WiFi/RTSP:**
```
UAV camera ──RTSP (WiFi riêng)──► laptop: cv2.VideoCapture("rtsp://<uav-ip>/stream")
Node telemetry (đt/laptop 2/ESP32) ──UDP 8888──► laptop (qua WireGuard tunnel nếu node chạy được WG client)
```

**Variant B — UAV downlink FPV 5.8GHz:**
```
UAV camera ──FPV 5.8G──► receiver USB (UVC) ──► laptop: cv2.VideoCapture(<index>)
Vị trí UAV: MAVLink (nếu B2=yes) / GPS onboard / mô phỏng 1Hz UDP 8888
Node telemetry (nếu có) ──UDP 8888 qua WiFi riêng (+WG nếu được)──► laptop
```

Quy tắc chung cả 2 variant: **mọi thứ đổ về UDP 8888 như cũ** — `TelemetryFeed`
(`tactical_telemetry_feed.py:31-82`) không đổi; WireGuard chỉ là tầng transport bên dưới.
Nếu node không chạy được WG client (ví dụ ESP32 giới hạn) → fallback: LAN WPA2 riêng,
ghi rõ lý do trong đồ án; AC5 bench trên 2 node đủ khả năng (điện thoại + laptop).

## Related Code Files

**Create**
- `tactical_video_source.py` — `open_video_source(kind, url) → cv2.VideoCapture` (webcam index / RTSP FFMPEG buffer nhỏ / UVC path / file); trả fps thực đo.
- `test_vpn_link.py` — bench AC5: node phát UDP 1Hz qua VPN → HUD nhận; sai vị trí <1m so sim; cắt link → stale ≤5s, không crash.
- `udp_position_sender.py` — script node: phát `{"id","lat","lon","t"}` 1Hz tới laptop (thay thế firmware ESP32 nếu không có phần cứng — B4; format đúng `hardware-bom.md` §5).
- `docs/network-setup-wireguard.md` — hướng dựng mạng: AP, config WG laptop (server 10.7.0.1) + node (client 10.7.0.2), lệnh verify.

**Modify**
- `heretic_phase4_hud.py` — thêm flag `--source`/`--source-url`; thay khối `cv2.VideoCapture(0)` (`:193-195`) bằng `open_video_source`; truyền `imgsz` hợp lý cho 360P.

**Delete** — không.

## Implementation Steps

1. **W5d1** — kiểm tra `plan.md`: UAV đã về tay? → đọc B1, chốt variant A/B, ghi quyết định
   vào file này. Chưa về → **sim-first**: node 2 = điện thoại/laptop 2, video source = file/webcam;
   khi UAV về (trước W9) chỉ đổi source, không đổi kiến trúc.
2. **W5d2** — dựng mạng riêng: Windows Mobile Hotspot (laptop làm AP) hoặc router có sẵn;
   WPA2; node tham gia; ping 2 chiều OK.
3. **W5d3** — WireGuard: laptop = server (app WireGuard / `wg-quick`, IP 10.7.0.1);
   node = client (Termux trên Android / laptop 2 / esp_wireguard nếu ESP32 — B4).
   `wg show` 2 peer active.
4. **W5d4** — `udp_position_sender.py` trên node (vị trí sim di chuyển, biết ground truth);
   chạy `python test_vpn_link.py` → PASS.
5. **W5d5** — link-loss drill: `wg-quick down` (hoặc tắt WiFi node) → assert
   `feed.fresh("uav")` = None sau ≤5s, HUD không crash.
6. **W6d1** — tạo `tactical_video_source.py`: 4 kind; RTSP dùng `cv2.CAP_FFMPEG` +
   `CAP_PROP_BUFFERSIZE=1`; in fps thực đo sau 100 khung.
7. **W6d2** — `heretic_phase4_hud.py`: thêm `--source`/`--source-url`; thay `:193-195`;
   với 360P truyền `imgsz=640` vào `model.track`.
8. **W6d3** — tune 360P: conf 0.4, imgsz 640 (native 640×360, không upscale); bench fps
   trên 3050; clip 360P có người → đo thời gian từ vào khung đến cảnh báo (<2s).
9. **W6d4** — update `docs/laptop-deployment-guide.md`: mục mạng riêng + `--source`.

## Success Criteria

- [ ] `wg show` (laptop) + lệnh tương đương trên node: 2 peer active; ping node <20ms
- [ ] `python test_vpn_link.py` PASS: HUD nhận position 1Hz qua VPN, sai <1m so sim;
      cắt link → local mode ≤5s, không crash — **AC5**
- [ ] `python heretic_phase4_hud.py --source rtsp --source-url rtsp://...`
      (hoặc `uvc`/`file` theo variant) chạy **≥15fps @360P** — **AC8** (nửa)
- [ ] Người trong khung 360P → cảnh báo HUD <2s (đo timestamp log) — **AC8** (nửa)
- [ ] `git diff tactical_telemetry_feed.py` rỗng — ràng buộc interface
- [ ] `docs/network-setup-wireguard.md` đủ để người khác dựng lại mạng từ 0

## Risk Assessment

| Rủi ro | Mitigation |
|--------|-----------|
| Node không chạy được WG client (ESP32 / điện thoại giới hạn) | Fallback LAN WPA2 riêng (vẫn là "mạng riêng", ghi trade-off trong đồ án); AC5 bench trên 2 node đủ khả năng (điện thoại + laptop) |
| RTSP lag/đứt (variant A) | `rtsp_transport;tcp`, buffer size 1; chấp nhận delay 1–2s và công khai trong đồ án |
| Không có 4G SIM (B7) | WiFi-only; demo site chọn trong vùng phủ AP; 4G chỉ là uplink dự phòng, không block kiến trúc |
| 360P <15fps | đóng app nặng, tắt hardware acceleration trình duyệt; nếu vẫn chưa đủ → `imgsz=480` + ghi nhận trade-off chất lượng |
| IP laptop đổi giữa các lần demo | DHCP reservation trên AP + tài liệu `network-setup-wireguard.md` ghi IP tĩnh |
| Receiver FPV (variant B) không nhận UVC | Verify **khi UAV về tay** (test cắm vào laptop); nếu không → yêu cầu đổi nguồn video hoặc dùng replay file (PDR §7 cho phép "replay video 360P") |
