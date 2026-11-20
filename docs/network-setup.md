# Network Setup — Mạng riêng + scrcp WiFi (W5)

Mục tiêu: laptop + phone (phi công) + node 2 (telemetry) trên **1 mạng WPA2 riêng**,
không phụ thuộc hạ tầng dân dụng. Video đi **scrcp TCP** qua mạng này, telemetry đi
**UDP 8888**. Đây là critical path của demo — bench theo mục 5 trước khi field test.

## Topology

```
Drone (Mini 2 SE) ──OcuSync 5.8GHz──► phone (DJI Fly)
Phone ──scrcp TCP (adb connect)──► laptop: capture frame (mss) → HUD
Node 2 (đt/laptop 2) ──UDP 8888──► laptop: TelemetryFeed (chấm xanh + UAV sim)
```

Tách băng tần: **OcuSync ép 5.8GHz** (DJI Fly: Settings → Transmission frequency)
vì hotspot Windows chỉ phát 2.4GHz — tránh tranh sóng với link drone.

## 1. Hotspot riêng (laptop làm AP)

- Settings → Network & internet → **Mobile hotspot** → bật, đặt mật khẩu WPA2.
- Lưu: IP hotspot Windows thường `192.168.137.1` (laptop).
- Giới hạn: **chỉ 2.4GHz**, hay drop client khi mang tải → nếu có router cũ, dùng
  router làm AP (WPA2, band 5GHz nếu được) — ổn định hơn, khuyến nghị cho ngày demo.

## 2. Phone phi công (video pipe)

1. Bật **USB debugging** (Settings → Developer options).
2. Cắm USB laptop → authorize ("Allow USB debugging").
3. Laptop: cài **scrcp** (tải `scrcp-win64` từ GitHub Genymobile/scrcpy, giải nén,
   không cần install) + `adb` cùng bundle.
4. `adb devices` → thấy phone. Bỏ cable, giữ phone trong mạng hotspot:
   `adb tcpip 5555` rồi `adb connect <ip-phone>:5555` (phone: Settings → About →
   Wi-Fi IP, thường `192.168.137.x`).
5. Chạy `scrcp.exe --max-size 1280` → window hiện feed phone trên laptop.
6. **Chứng nhận**: window scrcp phải chạy ≥30fps ổn định khi phone play video full-screen.

## 3. Node 2 (telemetry 1Hz)

Chạy `udp_position_sender.py` trên thiết bị thứ 2 (laptop 2 / điện thoại Termux):

```bash
.venv/bin/python udp_position_sender.py --target 192.168.137.1 --id ally-1
.venv/bin/python udp_position_sender.py --target 192.168.137.1 --id uav \
    --offset-m 40 --speed 3.0 --bearing 90   # mô phỏng UAV bay ngang 3 m/s
```

Laptop (HUD): `.venv/bin/python heretic_phase4_hud.py --telemetry` → chấm xanh
(ally) + chấm UAV hiện trên minimap.

## 4. Bench chất lượng mạng (W5d5 — làm TRƯỚC field test)

Điều kiện: phone play clip full-screen (hoặc bay i1 Pro thật) + `udp_position_sender`
chạy đồng thời. Đo và ghi:

| Metric | Ngưỡng | Cách đo |
|--------|--------|---------|
| FPS capture scrcp (mss) | ≥15fps ổn định | script capture in fps 10s |
| Packet loss UDP 8888 | ~0 | sender in timestamp; so với nhận |
| Latency video (photon→frame) | <0.6s | clip có đồng hồ/giây trên màn |
| Chạy 30 phút | không drop client | quan sát + log |

Không đạt → thử router làm AP 5GHz → vẫn không → ghi fallback (PDR §7 cho phép
replay video 360P qua `file`).

## 5. Link-loss drill (AC5)

1. HUD đang chạy `--telemetry`, ally + UAV hiện trên minimap.
2. **Tắt WiFi của node 2** (mô phỏng đứt link).
3. Quan sát: chấm ally mất sau **≤5s** (`STALE_AFTER_S`), HUD **không crash**,
   cảnh báo image-based (YOLO) vẫn hoạt động.
4. Bật lại WiFi → chấm quay lại trong ~1s.
5. Lặp với scrcp: tắt WiFi phone → HUD giữ frame cuối + (W8: banner MẤT LIÊN KẾT).

Verify nhanh trên server không cần laptop: `.venv/bin/python test_link_loss.py`
(7 checks: 1Hz + toa độ <1m + stale ≤5s + khôi phục).

## 6. Troubleshooting

| Triệu chứng | Nguyên nhân → xử lý |
|-------------|---------------------|
| `adb devices` rỗng | Chưa authorize USB / cable chỉ sạc → đổi cable, bấm lại authorize |
| `adb connect` refused | Phone không cùng mạng với laptop / sai IP → kiểm tra phone join hotspot |
| Window scrcp đen/đơ | Phone khóa màn → giữ màn sáng (Settings → Display → Screen timeout dài + Developer options → Stay awake while debugging) |
| Hotspot drop client | Giới hạn hotspot Windows → dùng router làm AP |
| Video drone giật khi có scrcp | OcuSync đang 2.4GHz tranh sóng → ép 5.8GHz trong DJI Fly |
| UDP không đến laptop | Sai IP target / firewall laptop chặn → `--target <ip-laptop>`, tắt firewall port 8888 |
