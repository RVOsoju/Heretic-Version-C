# Network Setup — Hướng dẫn chi tiết từng bước (laptop + iPhone)

**Mục tiêu cuối:** HUD chạy trên laptop, nhận video từ iPhone qua **AirPlay** (WiFi),
nhận vị trí đồng đội (node 2) qua **UDP 8888** — tất cả trên 1 mạng WPA2 riêng.
Đây là critical path của demo — làm theo thứ tự các Part dưới, mỗi Part có
**điểm kiểm tra** (✓) trước khi sang Part kế.

**Thời lượng:** ~1–1.5h (gồm 30 phút bench).
**Sửa 19/11:** phone là iOS → AirPlay (không scrcp/adb); node 2 = iSH trên iPhone.

```
Drone (Mini 2 SE) ──OcuSync 5.8GHz──► iPhone (DJI Fly)      [sau này, W9]
iPhone ──AirPlay (WiFi)──► laptop: window AirPlayReceiver → capture (mss) → HUD
iPhone (iSH) ──UDP 8888──► laptop: TelemetryFeed (chấm xanh trên minimap)
```

Tách băng tần (khi bay drone): **OcuSync ép 5.8GHz** trong DJI Fly
(Settings → Transmission frequency) vì hotspot Windows chỉ phát 2.4GHz.

---

## PART 0 — Chuẩn bị laptop (15 phút)

### 0.1 Cập nhật code

Mở Terminal (PowerShell/cmd) ở thư mục repo:

```powershell
cd C:\duong\dan\den\Heretic Version C
git pull
```

**✓ Kiểm tra:** không có lỗi; các file `udp_position_sender.py`,
`udp_receive_counter.py`, `tactical_video_source.py`, `bench_window_capture.py`
có trong thư mục.

### 0.2 Cài AirPlayReceiver (app nhận AirPlay trên Windows)

1. Mở: `https://github.com/stefand/airplayreceiver/releases`
2. Tải file `.zip` mới nhất (hàng `AirPlayReceiver v...`, file `win-x64`).
3. Giải nén ra 1 chỗ cố định, vd `C:\AirPlayReceiver\`.
4. Chạy `AirPlayReceiver.exe` → xuất hiện 1 **window đen** trên desktop.
5. **Để window mở — không đóng.**

**✓ Kiểm tra:** window AirPlayReceiver đang mở, không có báo lỗi.

### 0.3 Bật hotspot riêng

1. `Settings` → `Network & internet` → `Mobile hotspot`.
2. Bật `Mobile hotspot` = **On**.
3. Bấm `Edit` → đặt tên mạng: `heretic`, mật khẩu: `heretic123` (hoặc tự chọn).
4. Mở `cmd`, chạy:
   ```
   ipconfig
   ```
   Tìm mục `Wireless LAN adapter Local Area Connection*` → đọc dòng
   `IPv4 Address` — thường là **`192.168.137.1`**.

**✓ Kiểm tra:** **VIẾT CHỮA IP này ra giấy/note** — các Part sau dùng nó.
Nếu IP không phải 192.168.137.1 → thay mọi chỗ `192.168.137.1` trong doc
bằng IP thật của cậu.

---

## PART 1 — Chuẩn bị iPhone (15 phút)

### 1.1 Giữ màn hình luôn sáng

`Settings` → `Display & Brightness` → `Auto-Lock` → chọn **Never**.

### 1.2 Kết nối iPhone vào hotspot

`Settings` → `Wi-Fi` → chọn mạng **`heretic`** → nhập mật khẩu.

### 1.3 Cài iSH (terminal Linux trên iOS — chạy node 2)

1. Mở **App Store** → tìm **`iSH`** → `Get` (miễn phí).
2. Mở iSH → hỏi chọn hệ điều hành → chọn **Alpine Linux** → `OK`.
   Lần đầu cài ~1–2 phút, chờ tới khi hiện dòng lệnh `~ #`.
3. Gõ lệnh (chờ ~1–2 phút):
   ```
   apk add python3 curl
   ```

**✓ Kiểm tra:** sau lệnh trên, gõ `python3 --version` → hiện phiên bản Python.

### 1.4 Test AirPlay mirror

1. Trên iPhone: vuốt từ **góc trên-phải** xuống → mở **Control Center**.
2. Bấm icon **Screen Mirroring** (2 hình chữ nhật chồng nhau) — KHÔNG cần giữ.
3. Chọn **tên laptop** (dòng AirPlayReceiver) trong danh sách.
4. Window AirPlayReceiver trên laptop **phải hiện màn hình iPhone**.
5. Test: mở bất kỳ video nào trên iPhone → play full-screen →
   nhìn window trên laptop: **ổn định, không giật** (~30fps).

**✓ Kiểm tra:** window laptop hiện đúng màn iPhone, video chạy mượt.
(Nếu không thấy laptop trong danh sách → iPhone và laptop phải cùng 1 WiFi.)

---

## PART 2 — Node 2: chuyển 2 file + chạy sender (10 phút)

### 2.1 Laptop: bật file server (để iPhone tải 2 file)

Mở terminal ở thư mục repo (cùng chỗ Part 0.1), chạy:

```powershell
.venv\Scripts\python -m http.server 8000
```

**Để terminal này MỞ** (nó serve file cho iPhone qua hotspot).

### 2.2 iPhone (trong iSH): tải 2 file

Gõ 2 lệnh sau trong iSH (thay IP nếu Part 0.3 không phải 192.168.137.1):

```
curl -o udp_position_sender.py http://192.168.137.1:8000/udp_position_sender.py
curl -o tactical_telemetry_feed.py http://192.168.137.1:8000/tactical_telemetry_feed.py
```

**✓ Kiểm tra:** gõ `ls` → thấy 2 file trên.

### 2.3 iPhone (trong iSH): chạy sender

```
python3 udp_position_sender.py --target 192.168.137.1 --id ally-1
```

Chờ ~10s (iSH là emulator, Python khởi động chậm) → **phải hiện dòng mỗi 1 giây**:

```
[NODE] ally-1: phat 1/1s -> 192.168.137.1:8888 (bat dau 20m, 1.4 m/s, huong 90 do)
[   0.0s] ally-1 21.033320 105.733300
[   1.0s] ally-1 21.033320 105.733316
```

**✓ Kiểm tra:** dòng in ra mỗi giây. **Để iSH chạy nền** — cậu có thể
vuốt sang app khác, iSH vẫn phát tiếp.

---

## PART 3 — Smoke test: chấm xanh hiện trên HUD (5 phút)

Trên laptop (terminal ở thư mục repo):

```powershell
.venv\Scripts\python heretic_phase4_hud.py --telemetry
```

**✓ Kiểm tra (cả 3):**
1. Console hiện `[TELEMETRY] Dang nghe tin hieu GPS UDP port 8888`
2. Trên minimap HUD: **chấm xanh (ally)** hiện ở phía Bắc tâm (~20m)
3. Chấm xanh **di chuyển dần về Đông** (sim đi 1.4 m/s, hướng 90°)

Bấm `q` để thoát HUD. Nếu không có chấm xanh → xem bảng Troubleshooting cuối doc.

---

## PART 4 — Bench chất lượng mạng W5d5 (45–60 phút)

**Điều kiện đúng demo:** iPhone play clip full-screen + AirPlay + iSH sender
chạy **đồng thời**.

### 4.1 Chuẩn bị clip trên iPhone

- Clip bất kỳ, **có đồng hồ/giây rõ** trên màn là tốt nhất (để đo latency).
- Clip K2 trên laptop → gửi sang iPhone (OneDrive / email / Bluetooth).
- Mở clip, **play full-screen**, để AirPlay mirror bật.

### 4.2 Đo FPS capture (laptop)

**Đóng HUD trước** (nếu đang mở) — bench chạy độc lập.

```powershell
.venv\Scripts\python bench_window_capture.py --title AirPlay --duration 30
```

**Kết quả mong đợi:**

```
[BENCH] capture window chua 'AirPlay' trong 30s...
  t=  3.1s fps= 29.3
  ...
[BENCH] 870 khung / 30.0s = 29.0fps (ngưỡng ≥15), kich thuoc 1280x720
[BENCH] DONE
```

**✓ Đạt:** fps trung bình **≥15** và các mốc 3s không tụt sâu.

### 4.3 Đo packet loss UDP (laptop)

Vẫn giữ: clip đang play + AirPlay + iSH sender chạy. Chạy thêm:

```powershell
.venv\Scripts\python udp_receive_counter.py --duration 30
```

**✓ Đạt:** `packet loss 0.0%` (hoặc ≤ ~5% — gửi số thật cho tớ).

### 4.4 Ước lượng latency video (bằng mắt, ~1 phút)

Clip có đồng hồ: nhìn thời điểm kim giây chuyển trong clip vs thời điểm thấy
trên window AirPlay → ước lượng trễ.

**✓ Đạt:** **< 0.8s** (AirPlay chậm hơn scrcp, ngưỡng đã nới).

### 4.5 Chạy 30 phút không drop

Để **tất cả** (clip + AirPlay + iSH sender) chạy liên tục 30 phút:

```powershell
.venv\Scripts\python bench_window_capture.py --title AirPlay --duration 1800
```

**✓ Đạt:** không có lúc window đen/drop client, fps không tụt về 0.

---

## PART 5 — Link-loss drill — AC5 (10 phút)

### 5.1 Mất link UDP (node 2)

1. Laptop: chạy HUD `heretic_phase4_hud.py --telemetry`, chấm xanh hiện.
2. iPhone: vuốt lên giữa màn (app switcher) → **vuốt iSH RA NGOÀI** (kill sender).
3. **Quan sát HUD:** chấm xanh phải **biến mất sau ~5s**, HUD **không crash**,
   video + box detect vẫn chạy.
4. Mở iSH lại → chạy lại lệnh Part 2.3 → chấm xanh **quay lại trong ~1s**.

### 5.2 Mất link video (AirPlay)

1. Laptop: chạy `heretic_phase4_hud.py --source window --source-url AirPlay`
   (iPhone đang mirror clip).
2. iPhone: **tắt Wi-Fi** (Control Center → icon WiFi).
3. **Quan sát HUD:** phải **đơ tại frame cuối, không crash**
   (banner "MẤT LIÊN KẾT" sẽ có ở W8 — hiện tại chưa).
4. Bật lại Wi-Fi → video quay lại.

**✓ AC5 đạt khi cả 5.1 + 5.2 đúng như mô tả.**

---

## PART 6 — Gửi số liệu cho tớ

Gửi 5 con số (chụp màn hình console cũng được):

1. **FPS bench 30s** (Part 4.2)
2. **Packet loss %** (Part 4.3)
3. **Latency ước lượng** (Part 4.4)
4. **30 phút:** có drop không? fps có tụt không?
5. **Drill:** chấm mất sau bao nhiêu giây? (Part 5.1)

→ Tớ đóng AC5 + update plan/PDR/report. Sau đó sang W6d3: tune 360P + đo fps.

---

## Troubleshooting

| Triệu chứng | Nguyên nhân → xử lý |
|-------------|---------------------|
| Không thấy laptop trong danh sách AirPlay | iPhone + laptop khác mạng / AirPlayReceiver chưa chạy → iPhone join hotspot `heretic`, mở lại receiver |
| Window AirPlay đen/đơ | iPhone khóa màn → Part 1.1 (Auto-Lock: Never) |
| `apk add` trong iSH lỗi/không lên | Mạng iSH chưa sẵn → đóng mở iSH lại; vẫn lỗi → kiểm tra iPhone đã join hotspot |
| `curl` trong iSH không tải được file | Part 2.1 chưa chạy / sai IP → kiểm tra `python -m http.server 8000` đang mở, thay IP đúng |
| HUD không có chấm xanh | sender sai `--target` / firewall laptop chặn port 8888 → chạy lại Part 2.3 với IP đúng; tắt tạm Windows Firewall test |
| `bench_window_capture.py` báo "khong tim thay window" | AirPlayReceiver chưa mở / title sai → mở receiver, thử `--title AirplayReceiver` |
| Hotspot drop client khi chạy 30 phút | Giới hạn hotspot Windows → dùng router cũ làm AP 5GHz (settings WPA2, cùng tên `heretic`) |
| Video drone giật khi bay thật (W9) | OcuSync đang 2.4GHz tranh sóng → ép 5.8GHz trong DJI Fly |
