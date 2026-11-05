# Weekly Report — tổng hợp tuần 30/10–04/11 (W4 fine-tune XONG SỚM)

**Plan:** `plans/261015-1637-phase5-3-month-roadmap/`
**Mốc tuần:** W3 data + prep xong sớm 27–30/10 (report `weekly-261030-w3-report.md`) →
**W4 fine-tune 8 class XONG SỚM 30/10–04/11** (trước cửa sổ 09–15/11).
**Kế tiếp:** W5 = 16/11–22/11 — sim-first bench 2 node + WireGuard (không phụ thuộc UAV).

## 1. Đã làm

| # | Việc | Kết quả | Bằng chứng |
|---|------|---------|------------|
| W4d1 | Fine-tune **26n 100ep** (device 0,3, imgsz 640) | mAP50 **0.5557** — **plateau** (30→100ep chỉ +0.016) | val log, `yolo26n-military-8c.pt` |
| W4d2 | **Escalate 26s 100ep** (user chốt, dù bottleneck = data không phải capacity) | mAP50 **0.6315** (+0.076 vs 26n), 8/8 class lên | `yolo26s-military-8c-base.pt` |
| W4d3 | **Data lever (rebalance)**: box-level downsample `car` 0.3 / `person` 0.5 (TRAIN ONLY) + `copy_paste 0.3` → retrain **26s-rebal 100ep** | mAP50 **0.6314** (tổng flat) nhưng **mission class lên**: soldier 0.895, mil_vehicle 0.957, bus 0.586, boat 0.507, motorcycle 0.497, truck 0.368 — đổi lại car/person giảm (đúng trade) | `yolo26s-military-8c.pt` (RECOMMENDED), val fresh 04/11 |
| W4d4-prep | HUD thêm `--video` (test clip thật thay webcam) + in `[FPS]` mỗi 30 khung | smoke test pass; chạy được mọi resolution (đọc w/h khung đầu) | `heretic_phase4_hud.py` |
| W4d4-prep | **Doc hướng dẫn chạy laptop** (run-guide step-by-step) | `docs/laptop-verify-clip-test.md` | — |
| W4d4-prep | **Clip test pipeline trên server** (headless, 26s-rebal, `bus-360p.mp4`) | detect→track→distance→gater→alert→HUD chạy đúng; gater fire f03/f05/f12; tracking distance giảm-tăng đúng; **bus→boat+person** = known-issue 360p | 30 khung, 13.3fps (server) |
| W4d4 | **Clip test footage thật K2** (combat 720p, `yt-dlp`→`ffmpeg` H.264) | **`soldier` 2236 det** (Soledar aerial trench) + **`military_vehicle` 28 det, tank conf 0.73–0.81** (Tobrazky, 3 tank box đúng) — cả 2 class threat detect đúng trên combat footage | `assets/k2-*-detect-h264.mp4` (gitignored) |

## 2. Kết quả train (val fresh 04/11, weight 26s-rebal — RECOMMENDED)

| Class | mAP50 | mAP50-95 | Vai trò mission |
|-------|-------|----------|-----------------|
| **military_vehicle** | **0.957** | 0.706 | threat — ĐẠT |
| **soldier** | **0.895** | 0.576 | threat — ĐẠT |
| car | 0.752 | 0.503 | de-prioritized (0.3) |
| bus | 0.586 | 0.409 | threat phụ |
| motorcycle | 0.497 | 0.219 | threat phụ (yếu — data) |
| boat | 0.507 | 0.253 | threat phụ (yếu — data + domain gap COCO) |
| truck | 0.368 | 0.246 | threat phụ (yếu — data) |
| person | 0.489 | 0.216 | de-prioritized (0.5), dân thường |
| **all** | **0.631** | **0.391** | |

**Chuỗi mAP50:** 26n-30ep 0.5398 → 26n-100ep 0.5557 (plateau) → 26s-base 0.6315 → **26s-rebal 0.6314**.

## 3. Quyết định kỹ thuật (chốt tuần)

| Quyết định | Lý do |
|------------|-------|
| **26n plateau = data-limited, KHÔNG phải undertrained** | 30→100ep chỉ +0.016; class yếu (truck/motorcycle/bus/boat) thiếu data nhỏ-object aerial. Tăng epochs vô ích. |
| **mAP-tổng là SAI metric cho mission này** | car 41% + person 34% boxes (tốt ý de-prioritize) kéo tổng xuống; đo bằng **mission class** (soldier, mil_vehicle) mới đúng — cả 2 đạt cao. |
| **Data lever = box-level downsample (train only) + copy_paste** | car 0.3 / person 0.5 (val/test full-density → mAP unbiased); seeded `random.Random(0)` → reproducible. Không class-weighting trước (W3) — giờ mới tune sau khi thấy per-class. |
| **26s-rebal = weight demo chính** | soldier 0.895 + mil_vehicle 0.957 = 2 class threat mạnh nhất; trade car/person chấp nhận (không phải target cảnh báo). |
| **Gate mAP50 ≥0.75 KHÔNG đạt (0.631) — chấp nhận có lý do** | Dataset data-limited, không capacity. Mission class đạt. Push tổng nếu cần = thêm data class yếu (truck/motorcycle/boat) hoặc imgsz cao hơn (W6+), KHÔNG block demo. |
| **Không dùng Docker** | HUD realtime cần GPU (nvidia-docker) + webcam (`/dev/video0`) + display (X11) passthrough — phiền trên Win/WSL2. `requirements-lock.txt` đã đảm bảo env reproducible (server==laptop). Chỉ làm nếu giảng viên yêu cầu. |
| **Clip test server = chỉ verify pipeline** | Server 32GB Ada → FPS **tối ưu**, không đại diện laptop 4GB. Laptop mới là realtime ground truth (W4d4 tối nay). |

## 4. Kiểm thử & review

- **Val fresh (04/11):** 26s-rebal mAP50 0.6314 / mAP50-95 0.3908 (bảng §2) — số thật, không mock
- **Regression:** `test_telemetry_chain.py` 20/20 + `test_tracking.py` 7/7 (không đổi từ W2/W3)
- **Clip test server:** pipeline end-to-end chạy đúng; `person`→im lặng (đúng thiết kế) · `boat`→alert (threat class) · tracking + gater hoạt động; 1 khung HUD save verify layout (minimap + marker + banner)
- **Compile sạch** 3 file code sửa
- code-review `--model`/8-class (W3, `b27a3043`): PASS 0 critical — không thay đổi tuần này

## 5. Files (đã commit — user tự push)

- **Modify:** `train_military_yolo.py` (`--base`, `--copy-paste`, `run_name_for()`) · `prepare_heretic_8c_dataset.py` (downsample `DOWNSAMPLE`, `rng`) · `heretic_phase4_hud.py` (`--video`, FPS, đa-resolution) · `docs/laptop-verify-clip-test.md` (rewrite run-guide)
- **Weights (trackable, `weights/*.pt`):** `yolo26s-military-8c.pt` (rebal, **RECOMMENDED**) · `yolo26s-military-8c-base.pt` (fallback) · `yolo26n-military-8c.pt` (fallback nhẹ)
- `dataset/` + `runs/` — gitignored, **không commit**

## 6. Unresolved

1. **⚠ Realtime trên laptop chưa verify** — server 13.3fps (32GB) là optimistic. **Chờ user tối nay** chạy `--model weights\yolo26s-military-8c.pt --video <clip>` trên TUF F15 → đo FPS thật 4GB. Fallback sẵn: 26s-base → 26n → `--cpu`.
2. **⚠ False positive trên footage thật** (bạt/tarp → `boat`/`soldier`/`mil-vehicle`) — root cause = **DATA domain gap** (boat=COCO ground-level, soldier=blob nhỏ 3.4k, mil-vehicle=camo/covered), **KHÔNG phải 26s**. val mAP không bắt được (val cùng-domain train, thiếu tarp/debris negatives). **Fix = hard-negative mining** (extract tarp/debris frame K2 → label empty → re-merge → re-train). *Phần "thiếu clip soldier" đã đóng — có footage soldier+tank thật (K2).*
3. **mAP50 gate 0.75 miss (0.631)** — chấp nhận (data-limited). Nếu giảng viên ép tổng: thêm data truck/motorcycle/boat + imgsz 640→800 (W6+).
4. **bus↔boat lẫn @360p** — known issue, cần clip ≥640p hoặc data bus+boat rõ.
5. **Roboflow soldier ~4.8k** — hạ ưu tiên (soldier 0.895 đã mạnh, không cần).

## 7. W5 kế hoạch (16/11–22/11) — M3 prep: sim-first

| Ngày | Việc | Verify |
|------|------|--------|
| W5d1–2 | Bench 2 node (laptop + node 2) + WireGuard, `udp_position_sender.py` | `wg show` 2 peer; ping <20ms |
| W5d3–4 | `test_vpn_link.py` (AC5 phần bench) — không phụ thuộc UAV | PASS (HUD nhận position 1Hz) |
| (W4d4 carry) | **Laptop realtime verify + clip soldier thật** | FPS ≥15–20 @4GB; box `soldier`+`military_vehicle` |
