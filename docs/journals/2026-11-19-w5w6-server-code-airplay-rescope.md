# Xong code server W5 + W6: UDP sender, link-loss bench, video source abstraction — và cuộc pivot sang AirPlay

**Ngày**: 2026-11-19
**Mức độ**: Thấp (milestone thường, 1 pivot bắt buộc)
**Thành phần**: udp_position_sender.py (mới), test_link_loss.py (mới), docs/network-setup.md (mới), tactical_video_source.py (mới), bench_window_capture.py (mới), heretic_phase4_hud.py
**Trạng thái**: Đã xử lý (code server W5 + W6 xong; verify laptop chuyển sang 23/11)

## Đã xảy ra gì

Code server của cả 2 tuần đóng trong 1 ngày, kèm 1 quyết định đổi pipe video giữa tuần.

- **W5 (mạng riêng + link loss)**: `udp_position_sender.py` (95 dòng, thuần stdlib — json/math/socket/time) mô phỏng GPS node 2 ở 1Hz, phát đúng format gói của `tactical_telemetry_feed.py`. `test_link_loss.py` = bench AC5: link sống (1Hz + độ chính xác toạ độ), cắt link (stale + không crash + phục hồi). `docs/network-setup.md` = hướng dẫn setup laptop.
- **Pivot (quyết định user, 19/11)**: phone phi công là **iOS** và chỉ có 1 laptop. scrcp/adb chỉ chạy Android → loại. Pipe video giờ là **AirPlay** (screen mirroring native của iOS → app AirPlayReceiver open-source trên Windows → capture window đó theo title). Node 2 (UDP sender) chạy trong **iSH** (Alpine userland, App Store) trên *chính* iPhone đó — iOS không có Termux. WiFi-only giữ nguyên (phi công đứng xa laptop). Đồng bộ hết docs: network-setup.md viết lại, plan.md, phase-03, PDR.
- **W6 (tuần video source + 360P)**: `tactical_video_source.py` (119 dòng) trừu tượng 5 nguồn — `webcam / rtsp / uvc / file / window`; `window` = capture theo substring title bằng mss+pywin32 (chỉ Windows, DPI-aware, re-query rect mỗi khung vì window mirror có thể di chuyển/resize). `--source` / `--source-url` wire vào `heretic_phase4_hud.py`, ưu tiên `--video` > `--source` > webcam 0 (backward compat). `bench_window_capture.py` đo fps thực + kích thước khung của window mirror (ngưỡng ≥15).

## Kết quả kỹ thuật chính

- **test_link_loss.py 7/7 PASS** trên đường đi thật (PositionSim → UDP 8898 → TelemetryFeed): A) 3–4 gói trong 3.2s ở 1Hz, toạ độ feed sai <1m so ground truth; B) cắt link → `fresh()` = None sau **4.0s** (cửa sổ 3.5–5.3s quanh STALE_AFTER_S=5s), không crash, `relative_positions()` bỏ ally; C) feed nhận gói mới sau khi phục hồi.
- **Review**: 1 Important + 2 Minor, fix hết, re-verify 7/7. Cái Important là **race của ground truth**: check A so toạ độ feed với entry theo index thời gian của list sent[] — trên server bận, feed hoàn toàn có thể đang giữ *chu kỳ 1s trước*, nên check có thể fail vì timing chứ không phải lỗi code. Fix bằng cách match vị trí đã phát gần nhất trong không gian GPS (`test_link_loss.py:67`). 2 Minor: hằng số stale bị trùng (DRY) và 1 nút troubleshooting sai trong docs.
- **Window capture là nửa chưa test**: verify trên server được tới giới hạn của platform — py_compile OK, smoke kind `file` 640×360 OK, kind `window` raise ImportError sạch trên Linux (mss/pywin32 chỉ Windows, theo thiết kế), và chạy HUD headless `--source file` đi tới display boundary (cv2.imshow chỉ GUI — bình thường, server không có X). fps thật của window AirPlay là số đo laptop 23/11, không phải số đo server.

## Cuộc pivot AirPlay — giá phải trả

Điểm đau: scrcp được plan và viết docs một nửa trước khi ai xác nhận OS của phone. Fix code thì rẻ (chỉ đụng variant window-capture của W6, lúc đó chưa tồn tại) và 0 đồng (AirPlay + iSH = 0đ, không cable), nhưng phải viết lại network-setup.md, plan.md, phase-03, PDR trong cùng ngày. iSH là emulator x86 — Python khởi động ~10s — không vấn đề ở 1Hz, nhưng nghĩa là node 2 chỉ "đủ dùng", không tinh gọn. Rủi ro mở thật sự: fps mirror AirPlay **và** UDP 8888 cùng 1 WiFi, đồng thời, từ 1 phone — chưa bao giờ được đo. Đó là toàn bộ bench W5d5 vào 23/11.

## Bài học

- **Xác nhận platform trước khi plan pipe.** "Phone → adb/scrcp → laptop" nhìn platform-neutral trên giấy; thực ra không. Một câu fact của user (iOS, 1 laptop) đã thay hình dạng cả downlink. Chỗ rẻ nhất để hỏi là khi plan W5, không phải khi chạy W5.
- **Bench nào có thể fail vì timing thì đang đo máy, không đo code.** Fix nearest-match GT cùng họ với "full track lie" của W2 — check phải bền với async hợp lệ, nếu không nó đốt mất niềm tin vào những failure thật.
- Thời điểm trừu tượng hoá phát huy tác dụng: vì `tactical_video_source.py` chưa tồn tại, việc đổi scrcp→AirPlay chỉ là viết lại docs, không phải viết lại code. Thiết kế cho cái *sẽ thay đổi*, không phải cái tiện hôm nay.

## Tiếp theo

Thứ 2 23/11, laptop của user: setup hotspot + test mirror AirPlay (window AirPlayReceiver ổn định ≥30fps), bench mạng W5d5 (fps / packet loss / latency / 30 phút) + link-loss drill → **AC5**; sau đó W6d3/d4 tune 360P + đo ≥15fps → **M3**. Chưa commit — user tự commit/push theo quy tắc thường.
