# Network Setup — Mạng riêng + AirPlay WiFi (W5)

Mục tiêu: laptop + iPhone (phi công + node 2) trên **1 mạng WPA2 riêng**,
không phụ thuộc hạ tầng dân dụng. Video đi **AirPlay** (iPhone → AirPlayReceiver),
telemetry đi **UDP 8888**. Đây là critical path của demo — bench theo mục 4
trước khi field test.

> **Sửa 19/11:** phone là **iOS** → scrcp/adb không dùng được (Android-only) →
> **AirPlay** (screen mirroring native của iOS, 0đ). Quyết định WiFi-only giữ nguyên.

## Topology

```
Drone (Mini 2 SE) ──OcuSync 5.8GHz──► iPhone (DJI Fly)
iPhone ──AirPlay (WiFi)──► laptop: window AirPlayReceiver → capture frame (mss) → HUD
iPhone (iSH) ──UDP 8888──► laptop: TelemetryFeed (chấm xanh + UAV sim)
```

1 iPhone 2 vai: video DJI Fly + node 2 (iSH). Tách băng tần: **OcuSync ép 5.8GHz**
(DJI Fly: Settings → Transmission frequency) vì hotspot Windows chỉ phát 2.4GHz
— tránh tranh sóng với link drone.

## 1. Hotspot riêng (laptop làm AP)

- Settings → Network & internet → **Mobile hotspot** → bật, đặt mật khẩu WPA2.
- Lưu: IP hotspot Windows thường `192.168.137.1` (laptop).
- Giới hạn: **chỉ 2.4GHz**, hay drop client khi mang tải → nếu có router cũ, dùng
  router làm AP (WPA2, band 5GHz nếu được) — ổn định hơn, khuyến nghị cho ngày demo.

## 2. iPhone phi công (video pipe — AirPlay)

1. Laptop: cài **AirPlayReceiver** (open source: `github.com/stefand/airplayreceiver`,
   bản Windows, chạy exe — không cần install).
2. iPhone: kết nối WiFi hotspot.
3. iPhone: **Control Center** → **Screen Mirroring** (icon 2 hình chữ nhật chồng)
   → chọn laptop (AirPlayReceiver).
4. Màn iPhone hiện trong window AirPlayReceiver trên laptop.
5. **Chứng nhận**: window AirPlayReceiver chạy ≥30fps ổn định khi phone play
   video full-screen. Giữ màn sáng: Settings → Display & Brightness →
   Auto-Lock → Never.

## 3. Node 2 (telemetry 1Hz) — iSH trên chính iPhone

iSH = userland Alpine Linux trên iOS (App Store, 0đ), chạy được Python:

1. Cài **iSH** từ App Store.
2. Trong iSH: `apk add python3 curl`
3. Laptop (trong thư mục repo): `python -m http.server 8000` (serve 2 file).
4. Trong iSH:
   ```
   curl -o udp_position_sender.py http://192.168.137.1:8000/udp_position_sender.py
   curl -o tactical_telemetry_feed.py http://192.168.137.1:8000/tactical_telemetry_feed.py
   ```
5. Trong iSH: `python3 udp_position_sender.py --target 192.168.137.1 --id ally-1`

Laptop (HUD): `.venv/bin/python heretic_phase4_hud.py --telemetry` → chấm xanh
(ally) + chấm UAV hiện trên minimap.

Lưu ý: iSH là emulator x86 — Python khởi động chậm (~10s), không vấn đề cho 1Hz.

## 4. Bench chất lượng mạng (W5d5 — làm TRƯỚC field test)

Điều kiện: iPhone play clip K2 full-screen (hoặc bay i1 Pro thật) + sender iSH
chạy đồng thời. Đo và ghi:

| Metric | Ngưỡng | Cách đo |
|--------|--------|---------|
| FPS capture AirPlay (mss) | ≥15fps ổn định | `bench_window_capture.py` (tớ viết, 1 lệnh) |
| Packet loss UDP 8888 | ~0 | sender in timestamp; so với nhận |
| Latency video (photon→frame) | <0.8s | clip có đồng hồ/giây trên màn (AirPlay chậm hơn scrcp) |
| Chạy 30 phút | không drop client | quan sát + log |

Không đạt → thử router làm AP 5GHz → vẫn không → ghi fallback (PDR §7 cho phép
replay video 360P qua `file`).

## 5. Link-loss drill (AC5)

1. HUD đang chạy `--telemetry`, ally + UAV hiện trên minimap.
2. **Tắt sender** (vuốt iSH khỏi app switcher — mô phỏng đứt link UDP).
3. Quan sát: chấm ally mất sau **≤5s** (`STALE_AFTER_S`), HUD **không crash**,
   cảnh báo image-based (YOLO) vẫn hoạt động.
4. Bật lại sender → chấm quay lại trong ~1s.
5. Lặp với AirPlay: tắt WiFi iPhone → HUD giữ frame cuối + (W8: banner MẤT LIÊN KẾT).

Verify nhanh trên server không cần laptop: `.venv/bin/python test_link_loss.py`
(7 checks: 1Hz + toa độ <1m + stale ≤5s + khôi phục).

## 6. Troubleshooting

| Triệu chứng | Nguyên nhân → xử lý |
|-------------|---------------------|
| AirPlay không thấy laptop | iPhone + laptop khác mạng / AirPlayReceiver chưa chạy → iPhone join hotspot, mở receiver |
| Window AirPlay đen/đơ | iPhone khóa màn → giữ màn sáng (Auto-Lock: Never) |
| Hotspot drop client | Giới hạn hotspot Windows → dùng router làm AP |
| Video drone giật khi có AirPlay | OcuSync đang 2.4GHz tranh sóng → ép 5.8GHz trong DJI Fly |
| UDP không đến laptop | Sai IP target / firewall laptop chặn → `--target <ip-laptop>`, tắt firewall port 8888 |
| iSH chậm/không lên | Emulator x86, bình thường → chờ; iSH treo → khởi động lại app |
