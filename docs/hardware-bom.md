# Danh Sach Phan Cuong (BOM) - Heretic Version C

Trang thai: chua muac - chua duoc xac nhan so luong thuc te.
Ngay cap nhat: 2026-09-29

## 1. Danh sach linh phan

| # | Linh phan | So luong | Muc dich su dung | Ghi chu |
|---|-----------|----------|------------------|---------|
| 1 | Flycam (drone) co camera | 1 | Nod UAV: mang camera giai diem + bo phan GPS/ESP32 de tham chieu vi tri tu tren cao | FPV quad nho (2.5-5 inch) la du |
| 2 | GPS NEO-6M (5Hz, co anten patch) | 2 | (a) Gach tren flycam: vi tri UAV. (b) Mang theo lich: vi tri lich (`read_soldier_gps`) | Co san anten, khong can anten rieng |
| 3 | ESP32 DevKitC (WROOM-32, co WiFi) | 1 | Gach tren flycam: doc NMEA tu NEO-6M, broadcast UDP JSON 1Hz den laptop (nod `uav`) | Chi can 1 vi duy nhat flycam phat; lich doc truyen thong qua USB |
| 4 | Adapter USB TTL (CH340 hoac FTDI) | 1 | Nod lich: neu NEO-6M USB (FTDI) hoac doc thong qua USB TTL | Laptop nhan `/dev/ttyUSB0` |
| 5 | Buck converter 5V -> 3.3V (LM2596, 1A) | 1 | Nod flycam: cap 3.3V cho ESP32 + NEO-6M tu BEC 5V cua FC | Cap 500mA peak cua ESP32 WiFi |
| 6 | Tuyen tu 100uF + 10uF (ceramic) | 2 | Loc nguon: 100uF dau vao, 10uF dau ra buck, tranh ESP32 reset khi WiFi bat | |
| 7 | Duong day jumper (mau, duong that) | 1 bo | No day test tren breadboard | |
| 8 | Breadboard 830 diem | 1 | No test bo flycam truoc khi lap len drone | |
| 9 | Laptop co WiFi (cua lich) | 1 | Chay HUD + Ollama SLM + `TelemetryFeed` UDP port 8888 | Da co |
| 10 | Day USB Type-C / Micro-USB | 1 | No day / cap nang ESP32 khi test ban | |
| 11 | Battery 18650 + charger (tu chon) | 1 | Nuoc phan flycam khi bay xa BEC cua FC | Chi can neu BEC FC khong du ampe |

### Tu chon - cho tuong lai (WiFi khong che phuc duoc)

| # | Linh phan | So luong | Muc dich |
|---|-----------|----------|----------|
| 12 | Module LoRa SX1276 915MHz (M5Stack hoac RFM95) | 2 | Thay UDP khi bay ra ngoai pham vi WiFi: flycam + lich trao doi vi tri truc tiep, khong can mang |
| 13 | Anten LoRa 915MHz 3.5mm | 2 | Kem moi module LoRa tren |

## 2. No day nod FLYCAM (ESP32 + NEO-6M)

```
BEC 5V (FC flycam)  ---->  LM2596 (set 3.3V)
                              |
              3V3 <-----------+----------- 3V3  (NEO-6M)
              GND <-----------+----------- GND  (chung)
                              |
              ESP32 3V3 <-----+
              ESP32 GND

NEO-6M TX  --->  ESP32 GPIO16 (RX2)
NEO-6M RX  --->  ESP32 GPIO17 (TX2)
```

- No test tren breadboard truoc: day 5V tu adapter, kiem tra `serial monitor` co $GPRMC khong.
- Trong bay: NEO-6M dat tren diem cao nhat, anten patch huong len, khong che phia sau FC/mot den.
- Khoi luong them: ~25g (NEO-6M ~6g + ESP32 ~10g + day/nguon ~9g) - duoc voi quad 5 inch.

## 3. No day nod LICH (NEO-6M + laptop)

```
NEO-6M 5V  <---  USB laptop (5V)
NEO-6M TX  --->  USB TTL RX
NEO-6M GND  ---  USB TTL GND
```

- Chay: `python heretic_phase4_hud.py --telemetry --gps-port /dev/ttyUSB0`
- Neu chua co fix GPS trong nha: dung `--soldier-gps 21.0333,105.7333` thay the.

## 4. Firmware ESP32 (cach bai khi co may)

Firmware rieng (Arduino/C++) - chua viet, se viet khi co ESP32. Gioi han can thuc hien:

- Doc UART 9600 baud, parse `$GPRMC` (chinh xac giuong `tactical_telemetry_feed.py:_nmea_coord`).
- 1Hz: `WiFi UDP send` JSON den IP laptop, port 8888:
  `{"id": "uav", "lat": 21.0333, "lon": 105.7333, "t": 1727600000.12}`
- IP laptop: gan dong IP (static DHCP) de ESP32 khong mat lien ket.
- `TelemetryFeed` da co san: tin hieu > 5s coi la mat (`STALE_AFTER_S`), dot tren minimap bi xoa tu dong.

## 5. Nguyen tac phan loai dong doi (da thiet ke trong code)

- Co tin hieu GPS moi (< 5s) trong ban kinh 8m quanh muc tieu duoc YOLO phat hien
  -> **dong doi**: ve xanh, khong bat canh bao SLM.
- Khong co -> **dich**: ve do, bat canh bao theo ngat ngan (100m / 10m / 1m).
- Cod: `is_friendly_by_gps()` trong `tactical_telemetry_feed.py`, duoc kep vao
  `heretic_phase4_hud.py` qua flag `--telemetry`.

## 6. Chi phi tham khao (VND, gia 2026)

| Nhom | Uoc tinh |
|------|----------|
| NEO-6M x2 | 250k - 400k |
| ESP32 DevKitC | 100k - 150k |
| USB TTL CH340 | 30k - 50k |
| LM2596 + tuyen tu + day + breadboard | 100k - 150k |
| 18650 + charger (tu chon) | 100k - 200k |
| LoRa x2 + anten (tu chon) | 300k - 500k |
| **Tong (khong goi flycam/laptop)** | **~1M - 1.5M VND** |
