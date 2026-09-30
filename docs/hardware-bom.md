# Danh sách phần cứng (BOM) — Heretic Version C

**Trạng thái:** chưa mua — cần xác nhận trước khi đặt hàng.
**Ngày cập nhật:** 2026-09-30

Hệ thống gồm 3 node:

```
┌─────────────────────┐      WiFi (UDP 8888)      ┌──────────────────────────┐
│   FLYCAM (UAV)      │ ─────────────────────────> │   LAPTOP CỦA LÍNH        │
│   ESP32 + NEO-6M    │      JSON 1Hz             │   HUD + SLM + Telemetry  │
└─────────────────────┘                           └──────────────────────────┘
                                                        ^
                                                        │ USB TTL (NMEA)
                                               ┌──────────────────────────┐
                                               │   LÍNH: NEO-6M           │
                                               └──────────────────────────┘
```

- **Flycam**: mang camera giám sát + bo ESP32/NEO-6M, phát vị trí của chính nó (node `uav`) qua WiFi.
- **Lính**: mang NEO-6M, nối thẳng về laptop qua USB TTL để xác định vị trí trung tâm (cùng cơ chế `read_soldier_gps()` đã viết sẵn).
- **Laptop**: chạy HUD (Phase 4), SLM cảnh báo (Ollama) và listener UDP nhận vị trí UAV + các đồng đội.

> **Nguyên tắc phân loại:** ai mang module GPS có tín hiệu tươi (< 5 giây) và nằm trong bán kính 8 m quanh mục tiêu YOLO phát hiện → **đồng đội** (vẽ xanh, không cảnh báo). Ngược lại → **địch** (vẽ đỏ, cảnh báo theo ngưỡng 100 m / 10 m / 1 m).

---

## 1. Danh sách linh kiện chính

| # | Linh kiện | Số lượng | Mục đích sử dụng | Ghi chú |
|---|-----------|----------|------------------|---------|
| 1 | Flycam (drone) có camera giám sát | 1 | Node UAV: mang camera + bo ESP32/NEO-6M làm tham chiếu vị trí từ trên cao | FPV quad 2,5–5 inch là đủ |
| 2 | GPS NEO-6M (5 Hz, kèm anten patch) | 2 | (a) Gắn flycam → vị trí UAV. (b) Mang theo lính → vị trí lính (`read_soldier_gps()`) | Ra toạ độ sau ~10–30 s có trời; baud 9600, NMEA `$GPRMC` |
| 3 | ESP32 DevKitC (WROOM-32, WiFi 2,4 GHz) | 1 | Gắn flycam: đọc NMEA từ NEO-6M, broadcast UDP JSON 1 Hz tới laptop | Chỉ flycam cần phát; bên lính đọc theo UART nên không cần thêm |
| 4 | Adapter USB TTL (CH340 hoặc FTDI) | 1 | Node lính: cầu nối NEO-6M ↔ laptop; nhận `/dev/ttyUSB0` trên Linux | Dùng cho cả test bàn và field |
| 5 | Buck converter 5 V → 3,3 V (LM2596, 1 A) | 1 | Node flycam: lấy 3,3 V từ BEC 5 V của FC để cấp cho ESP32 + NEO-6M | Phải chịu peak ~500 mA khi ESP32 phát WiFi |
| 6 | Tụ lọc 100 µF (điện giải) + 10 µF (ceramic) | 2 | Lọc nguồn: 100 µF đầu vào, 10 µF đầu ra của buck — chống ESP32 tự reset khi bật WiFi | Bắt buộc, ESP32 rất nhạy nhiễu nguồn |
| 7 | Dây jumper (màu, đực-thực, đủ loại) | 1 bộ | Nối mạch test trên breadboard | ~40 sợi là đủ |
| 8 | Breadboard 830 điểm | 1 | Gắn thử toàn bộ bo flycam trước khi lắp lên drone | Test ở bàn với nguồn 5 V ngoài |
| 9 | Laptop có WiFi | 1 | Chạy HUD + Ollama SLM + `TelemetryFeed` (UDP port 8888) | Đã có |
| 10 | Cáp USB Type-C / Micro-USB | 1–2 | Nạp firmware và cấp nguồn khi test ESP32 trên bàn | — |
| 11 | Pin 18650 + sạc (tùy chọn) | 1 | Cấp nguồn flycam khi bay xa, BEC của FC không đủ dòng | Chỉ cần nếu FC không có BEC 5 V/2 A |

## 2. Tuỳ chọn — cho tương lai (vượt ngoài phạm vi WiFi)

| # | Linh kiện | Số lượng | Mục đích |
|---|-----------|----------|----------|
| 12 | Module LoRa SX1276 915 MHz (M5Stack hoặc RFM95) | 2 | Thay UDP khi bay ra ngoài vùng phủ WiFi: flycam ↔ lính trao đổi vị trí trực tiếp, không cần mạng |
| 13 | Anten LoRa 915 MHz (jack 3,5 mm) | 2 | Kèm mỗi module LoRa ở trên |

> Khi cần LoRa, `TelemetryFeed` giữ nguyên — chỉ thêm tầng nhận LoRa rồi đổ dữ liệu vào cùng dict `_latest`.

---

## 3. Sơ đồ nối — Node FLYCAM (ESP32 + NEO-6M)

```
BEC 5 V (FC flycam) ──► LM2596 (vặn ra 3,3 V)
                            │
             3V3 ◄──────────┼────────── 3V3  (NEO-6M VCC)
             GND ◄──────────┼────────── GND  (chung mass)
                            │
             ESP32 3V3 ◄────┘

NEO-6M TX  ──►  ESP32 GPIO16 (RX2)
NEO-6M RX  ──►  ESP32 GPIO17 (TX2)
NEO-6M GND ──►  ESP32 GND
```

**Ngân sách nguồn (3,3 V):**

| Thiết bị | Dòng trung bình | Dòng peak |
|----------|-----------------|-----------|
| ESP32 (WiFi) | ~180 mA | ~500 mA |
| NEO-6M | ~40 mA | ~50 mA |
| **Tổng** | **~220 mA** | **~550 mA** |

→ LM2596 1 A là dư; BEC 5 V của FC cần ≥ 1,5 A.

**Quy tắc lắp trên drone:**

1. Test trên breadboard trước: cấp 5 V từ adapter, mở Serial Monitor 9600 baud — phải thấy dòng `$GPRMC` liên tục mới được lắp lên.
2. NEO-6M đặt ở điểm cao nhất của flycam, anten patch hướng **lên trời**, không đặt sau FC, mô-tơ hay pin (nhiễu + che tín hiệu).
3. Cáp ngắn, gọn; gá bo ESP32 phía dưới, không che anten GPS.
4. Khối lượng thêm: ~25 g (NEO-6M ~6 g + ESP32 ~10 g + nguồn/dây ~9 g) — an toàn cho quad 5 inch.

## 4. Sơ đồ nối — Node LÍNH (NEO-6M + laptop)

```
Laptop USB (5 V) ──► NEO-6M VCC
NEO-6M TX  ──►  USB TTL RX
NEO-6M GND ──►  USB TTL GND
```

**Cách dùng trong code:**

```bash
# Khi có phần cứng:
python heretic_phase4_hud.py --telemetry --gps-port /dev/ttyUSB0

# Khi chưa có GPS (trong nhà):
python heretic_phase4_hud.py --telemetry --soldier-gps 21.0333,105.7333
```

- `--telemetry`: bật listener UDP port 8888 (nhận `uav` + các đồng đội) + bật nhận biết đồng đội.
- `--gps-port`: đọc toạ độ lính từ NEO-6M qua serial.
- `--soldier-gps`: khai báo toạ độ lính thủ công (test không cần phần cứng).
- Nếu GPS chưa có fix (trong nhà): code in cảnh báo và tự fallback về toạ độ mặc định.

## 5. Yêu cầu firmware ESP32 (viết khi có máy)

Firmware riêng (Arduino/C++) — **chưa viết**, sẽ viết ngay khi có ESP32. Giao diện bắt buộc phải khớp `tactical_telemetry_feed.py`:

1. Đọc UART **9600 baud**, parse `$GPRMC` (đúng logic `_nmea_coord()` đã có sẵn trong code — có mẫu để sao chép).
2. Mỗi **1 giây** gửi 1 UDP datagram JSON đến **IP laptop, port 8888**:

   ```json
   {"id": "uav", "lat": 21.0333, "lon": 105.7333, "t": 1727600000.12}
   ```

   - `id`: `"uav"` (hoặc id của đồng đội nếu sau này gắn thêm node).
   - `t`: timestamp giây (epoch) tại thời điểm phát.
3. **Gán IP tĩnh cho laptop** (DHCP reservation trong router) để ESP32 không mất liên kết khi IP đổi.
4. Nếu GPS chưa fix (trường `GPRMC` = `V`/`N`): **không gửi**, tránh phủ vị trí cũ bằng dữ liệu rác.

> Bên nhận (`TelemetryFeed`) đã tự xử lý: tín hiệu > 5 giây coi là mất, chấm trên minimap tự biến mất, không cần firmware lo.

## 6. Quy trình test khi phần cứng về

1. **Bàn làm việc:** NEO-6M + USB TTL → laptop. Chạy `read_soldier_gps()` — thấy `(lat, lon)` là qua.
2. **Bo flycam:** breadboard 5 V → LM2596 → ESP32 + NEO-6M. Serial Monitor thấy `$GPRMC`. Nạp firmware dummy gửi UDP 1 Hz.
3. **Mô phỏng end-to-end:** laptop chạy `heretic_phase4_hud.py --sim --telemetry`; ESP32 (hoặc script giả lập) phát UDP → chấm UAV/dồng đội xuất hiện đúng vị trí trên minimap.
4. **Bay:** lắp lên flycam, bay vòng quanh vị trí đứng, quan sát chấm UAV di chuyển đúng quỹ đạo; đứng cạnh đồng đội mang GPS → mục tiêu YOLO chuyển xanh, SLM im lặng.

---

## 7. Chi phí tham khảo (VND, giá 2026)

| Nhóm | Ước tính |
|------|----------|
| NEO-6M × 2 | 250k – 400k |
| ESP32 DevKitC | 100k – 150k |
| USB TTL CH340 | 30k – 50k |
| LM2596 + tụ + dây + breadboard | 100k – 150k |
| 18650 + sạc (tùy chọn) | 100k – 200k |
| LoRa × 2 + anten (tùy chọn) | 300k – 500k |
| **Tổng (không gồm flycam/laptop)** | **~1 – 1,5 triệu VND** |
