---
title: "Heretic C Phase 5 - 3-month roadmap (no budget, WiFi/4G VPN, 360P UAV)"
description: "Lộ trình 12 tuần cho đồ án Heretic C: tracking + YOLO 8 class + mạng riêng VPN + UAV 360P + demo E2E, ngân sách 0 đồng mua mới."
status: pending
priority: P1
effort: "12w"
branch: "main"
tags: [roadmap, phase5, 3-month, no-budget, uav, vpn, yolo]
blockedBy: []
blocks: []
created: "2026-10-15T09:41:57.389Z"
createdBy: "ck:plan"
source: skill
---

# Heretic C Phase 5 — Lộ trình 3 tháng (12 tuần)

## Overview

Kế hoạch thực thi Phase 5 (definition of done của đồ án) trong đúng 12 tuần, ngân sách 0 đồng:
chỉ dùng laptop TUF F15 (runtime), server 4× RTX 5000 Ada (fine-tune), UAV được cấp (camera 360P+).
Mỗi tuần có 1 deliverable đo được; mọi điểm mù được ghi nhận và có deadline giải quyết.
Nguồn scope: `docs/project-overview-pdr.md` (S1–S7, AC1–AC11).

**Giới hạn cứng (quyết định 2026-10-15):** không LoRa, không E88 Pro, không haptic (AC4 fallback = flash HUD + SLM),
không thermal. TelemetryFeed interface (UDP 8888, JSON `{id,lat,lon,t}`) giữ nguyên.

## 12-week roadmap

| Tuần | Ngày | Deliverable | Verify |
|------|------|-------------|--------|
| **W1** | 19/10–25/10 | Bật ByteTrack (`track=True, bytetrack.yaml` trên yolo26n); test 360P bằng video **tổng hợp** (downscale 720p → 640×360) — **UAV chưa rõ ngày về, W1 thuần code** | `model.track()` trả `boxes.id` ổn định trên clip 30s; log precision 360P (B6 bước 1) |
| **W2** | 26/10–01/11 | Velocity + approach speed; gater re-key theo `track_id`; `test_tracking.py` → **M1 done** | AC1: re-ID <5%/100 khung · AC2: sai vận tốc <10% · AC3: cắt ngưỡng 100m 1 lần → báo đúng 1 lần |
| **W3** | 02/11–08/11 | Tải MVRSD (verify Baidu; fallback AMAD/InvictusRex) + **VisDrone** (góc drone: person + 4 xe); **verify tham số thu** (độ cao/tốc độ/FOV) từ dataset card; prep data, map 8 class; **research nguồn `soldier`** (B9 — ưu tiên footage UAV tự quay) | `mvrsd-8c.yaml` hợp lệ, 3000 ảnh trên server; VisDrone subset 5 class; **tham số thu UAV ghi vào report**; B9 có kết quả |
| **W4** | 09/11–15/11 | Fine-tune yolo26n → 8 class (MVRSD + **VisDrone** + `soldier` + COCO regression) + regression check → **M2 done** | `yolo val` mAP50 ≥0.75 (val MVRSD+VisDrone); mAP 6 class COCO giảm ≤5 điểm; tham số thu UAV ghi báo cáo (AC7) |
| **W5** | 16/11–22/11 | **Sim-first**: dựng bench 2 node (laptop + node 2) + WireGuard, `udp_position_sender.py` — không phụ thuộc UAV | `wg show` 2 peer active; ping <20ms; `test_vpn_link.py` PASS (AC5 phần bench) |
| **W6** | 23/11–29/11 | Video source abstraction (`--source webcam/rtsp/uvc/file`); hiệu chỉnh YOLO cho 360P → **M3 done** | ≥15fps @360P; người trong khung → cảnh báo <2s (nửa AC8) |
| **W7** | 30/11–06/12 | Cone FOV trên minimap + **badge target trong/ngoài tầm nhìn** + tuần tra + **chế độ follow target** (MAVLink nếu hỗ trợ, nếu không = route gợi ý tay + HUD chỉ hướng) | `--sim` lộ trình waypoint: cone đúng hướng, **UAV bay theo vị trí mục tiêu** (AC6 sim) |
| **W8** | 07/12–13/12 | Tích hợp full: telemetry qua VPN, 3 chế độ degradation (full/position-only/local), link-loss test → **M4 done** | AC6 (bay thật nếu được, nếu không sim+bench); AC8: 10 phút live ổn định; cắt link → local ≤5s không crash |
| **W9** | 14/12–20/12 | Field test 1 với UAV được cấp (5 kịch bản, ghi log + video) | Log: 5/5 kịch bản chạy, issue list đã triage (critical/minor) |
| **W10** | 21/12–27/12 | Stress: VRAM 4GB, link loss, latency + fix | AC9: <3.8GB/30s, OOM → `--cpu` khởi động lại OK; 5 vòng cắt/ghép link ≤5s |
| **W11** | 28/12–03/01 | Demo end-to-end 10 phút (kịch bản PDR §7) + 2 buổi rehearsal | AC11: 1 lượt chạy không interrupt, có ghi hình; re-verify AC1–AC11 |
| **W12** | 04/01–10/01 | Tài liệu đồ án (cập nhật `docs/`, báo cáo cuối) + buffer | `docs/` đồng bộ (deployment + VPN, PDR status, BOM status); báo cáo đồ án đủ bảng kết quả AC1–AC11 |

## Sơ đồ hệ thống

```
                    MẠNG RIÊNG (WiFi/4G) + WireGuard
  ┌────────────────────────────┐          ┌─────────────────────────────────────────────┐
  │  UAV ĐƯỢC CẤP (360P+)      │          │  LAPTOP C2 — TUF F15 (RTX 3050 4GB, Win11)  │
  │                            │  video   │                                             │
  │  camera ───────────────────┼─────────►│  YOLO 8c + ByteTrack → TrackStore          │
  │   variant A: RTSP qua WiFi │          │    → gater (key = track_id) → SLM qwen2.5  │
  │   variant B: FPV 5.8G → UVC│          │    → HUD OpenCV: box + minimap + cone FOV  │
  │                            │ position │  TelemetryFeed UDP :8888 (interface giữ    │
  │  GPS / MAVLink ────────────┼─────────►│  nguyên, TTL 5s = STALE_AFTER_S)           │
  └────────────────────────────┘  1Hz     └─────────────────────────────────────────────┘
                                    JSON
  ┌────────────────────────────┐          ┌─────────────────────────────────────────────┐
  │  LÍNH                      │          │  NODE GPS ĐỒNG ĐỘI (tuỳ chọn)               │
  │  NEO-6M ── USB TTL ────────┼─────────►│  UDP 8888 {id, lat, lon, t} → chấm xanh     │
  │  (vị trí tâm HUD)          │          │  trên minimap, không bị cảnh báo            │
  └────────────────────────────┘          └─────────────────────────────────────────────┘
```

3 chế độ degradation: **FULL** (video + vị trí) / **POS-ONLY** (mất video, còn vị trí) / **LOCAL** (mất mọi link,
dữ liệu cũ >5s tự vô hiệu — cơ chế `STALE_AFTER_S` đã có ở `tactical_telemetry_feed.py:23`).

## Register điểm mù (blind spots)

| # | Điểm mù | Impact | Khi nào hết mù | Cách giải quyết |
|---|---------|--------|----------------|-----------------|
| B1 | **Downlink video UAV** (FPV 5.8G / WiFi RTSP / USB?) | Định hình variant video W6 (A: RTSP / B: UVC); W5–W4 không phụ thuộc | **Ngày UAV về (chưa rõ) + 1 tuần** | Mở hộp, đọc spec, test kết nối 10 phút; ghi kết quả vào đây; tới trước W9 (field test) |
| B2 | **MAVLink/GCS** của UAV | W7: upload waypoint tự động (variant A) vs bay tay theo route gợi ý (variant B — build trước) | **Ngày UAV về (chưa rõ) + 1 tuần** | Cắm radio telemetry + QGroundControl |
| B3 | **Vị trí UAV** (GPS onboard / MAVLink?) | Không có → demo dùng vị trí mô phỏng, AC6 đạt qua sim | **Ngày UAV về (chưa rõ) + 1 tuần** | Kiểm tra link telemetry / GPS onboard |
| B4 | Node ESP32+NEO-6M trong BOM **chưa mua** (`hardware-bom.md` ghi "chưa mua") | Không có node GPS vật lý → demo dùng `--soldier-gps` + đồng đội mô phỏng | W1 | Đếm kho; nếu không có → dùng đường sim (code đã hỗ trợ) |
| B5 | **MVRSD qua Baidu pan** — server có truy cập không? | Trễ 1 tuần W3 → W4 trôi | W3 (ngày 1) | Test tải 1 file trên server; fallback AMAD / InvictusRex (GitHub release) |
| B6 | **Chất lượng 360P** (người 20m ≈ 40–60px) | Detection rớt → phải tune imgsz/NMS ở W6 | W1 (video tổng hợp); retest frame thật khi UAV về | Chạy yolo26n trên 10 frame 640×360, log precision |
| B7 | **SIM 4G** có sẵn không | Không có → chỉ WiFi (tầm ngắn), demo phải trong vùng phủ AP | W5 | Kiểm tra kho; không ảnh hưởng kiến trúc (4G là uplink dự phòng) |
| B9 | **Nguồn ảnh class `soldier`** (dataset mở hay tự ghi footage thao trường?) | Không có → không fine-tune được class `soldier` (chỉ còn `person`) | W3d3 | Research dataset mở (GitHub); phương án dự phòng: tự ghi + label footage thao trường (cần đồng ý); nếu không có → escalate giảng viên (giữ 7 class) |

## KPI (acceptance criteria — PDR §5)

| AC | Tiêu chí | Verify | Ngưỡng pass |
|----|----------|--------|-------------|
| AC1 | Track ID ổn định | `test_tracking.py` trên video sim | ≥100 khung, re-ID <5% |
| AC2 | Tốc độ tiếp cận | Cùng script, so với ground truth sim | Sai <10% |
| AC3 | Gater theo track_id + target gần nhất | `test_telemetry_chain.py` (update) | Cắt ngưỡng 100m 1 lần → báo đúng 1 lần; 3 target → SLM chọn gần nhất, câu có khoảng cách + hướng |
| AC4 | Cảnh báo im lặng (fallback) | gater trigger → HUD flash | Flash <100ms, không phát âm |
| AC5 | Mạng riêng VPN | `test_vpn_link.py`: 2 node WiFi + WireGuard | HUD nhận position 1Hz, sai <1m so sim; đứt link → local ≤5s, không crash |
| AC6 | UAV patrol + FOV + follow | `--sim` lộ trình waypoints + target di động (bay thật ở W8) | Cone FOV đúng hướng; **UAV sim bay theo vị trí target**; badge trong/ngoài tầm nhìn đúng |
| AC7 | YOLO 8 class (góc UAV) | `yolo val` val MVRSD+VisDrone + 1 clip có lính + xe quân sự | mAP50 ≥0.75; `soldier` + `military_vehicle` được box + SLM cảnh báo; mAP 6 COCO giảm ≤5 điểm; weight chạy trên 3050 (pin version ultralytics server=laptop); **tham số thu (độ cao/tốc độ/FOV) ghi báo cáo** |
| AC8 | UAV được cấp live | Video 360P+ → HUD | ≥15fps; người trong khung → cảnh báo <2s |
| AC9 | VRAM 4GB | `nvidia-smi -l 1` 30s đầu chạy full; cố tình OOM | <3.8GB ổn định; `--cpu` khởi động lại bình thường |
| AC10 | SLM | Log `--sim` | <1.5s/call (warm); câu ≤12 từ, tiếng Việt |
| AC11 | Demo end-to-end | Kịch bản 10 phút (PDR §7) chạy 1 lượt | Không interrupt; đủ kênh cảnh báo |

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Tracking and gater track_id](./phase-01-tracking-and-gater-track-id.md) | Pending |
| 2 | [YOLO 8-class fine-tune MVRSD](./phase-02-yolo-8-class-fine-tune-mvrsd.md) | Pending |
| 3 | [Private network VPN and 360P camera](./phase-03-private-network-vpn-and-360p-camera.md) | Pending |
| 4 | [FOV patrol and integration](./phase-04-fov-patrol-and-integration.md) | Pending |
| 5 | [Field test demo and docs](./phase-05-field-test-demo-and-docs.md) | Pending |

## Dependencies

- **P1 → P4** — tracking feed cho integration; kết quả 360P (B6 bước 1) định hướng tune W6.
- **P2 độc lập với P1** — chạy song song trên server (W3–W4), không đụng file của P1.
- **P2 → P5** — model 8 class dùng trong demo W11.
- **P3 → P4** — integration cần VPN + camera 360P đã có.
- **P4 → P5** — field test/demo trên hệ tích hợp xong.
- **Ngoại bộ:** UAV về tay — gate B1–B3, **chưa rõ ngày về** (2026-10-15); chỉ block khối W5–W8 (variant video W6 + bay thật W8/W9), **W1–W4 không bị block** (sim-first); quyền truy cập Baidu (gate B5, khối W4); nguồn ảnh `soldier` (gate B9, khối W4 train).

## Open questions

1. **UAV được cấp về tay ngày nào** (chưa rõ, 2026-10-15) + **downlink video** là loại gì (FPV 5.8GHz / WiFi RTSP / USB)? → quyết định thiết kế W5–W8 — verify khi nhận máy; trước đó build sim-first.
2. UAV có hỗ trợ **MAVLink/GCS** (tuần tra tự động) không? → variant A/B tuần tra W7.
3. Có sẵn **SIM 4G/data** nào không? → nếu không: chỉ WiFi riêng (demo trong vùng phủ AP).
4. Module rung (haptic) có được cấp thêm sau này không? → giữ blocked; AC4 fallback flash + SLM.
5. **Nguồn ảnh class `soldier`** (B9) — dataset mở hay tự ghi footage thao trường? → research W3, chốt trước train W4.

## Validation Log

### Session 1 — 2026-10-15 (validate-workflow, interview)

**Trigger:** user chọn `/ck:plan validate` sau khi plan được tạo.

**Câu hỏi + câu trả lời (verbatim ý chính):**

1. *UAV được cấp về tay khi nào?* → **"Chưa rõ/chậm hơn"** (chậm hơn W1 dự kiến).
2. *Field test có chỗ bay rõ ràng không?* → **"Có chỗ bay rõ ràng"** (không cần escalate).
3. *8 class cuối cùng là gì?* → **chốt mới:** nhận diện `person` (người thường) và `soldier` (lính); xe: `car, motorcycle, truck, bus, boat` giữ nguyên + gộp toàn bộ xe quân sự thành 1 class `military_vehicle`; **loại máy bay các loại; không nhận diện cụ thể loại xe quân sự** (tăng/IFV/pháo → `military_vehicle`).
4. *Fine-tune trên server — tài nguyên GPU?* → **"Được khóa nhiều GPU, nhưng nên đẩy nhanh fine-tune và training YOLO26, và đảm bảo chọn đúng và đủ phiên bản của YOLO26 để sau khi training khi clone dự án về laptop cá nhân (RTX 3050 4GB VRAM và Intel i7 12700F) có thể chạy được"** → multi-GPU + **pin version ultralytics (server == laptop)**.

**Decisions confirmed (đóng):**
- W1–W4 **không** phụ thuộc UAV → sim-first; UAV là gate cho khối W5–W8 (variant video W6, bay thật W8/W9).
- Class list 8c = `person, soldier, car, motorcycle, truck, bus, boat, military_vehicle` (PDR S5 + AC7 đã cập nhật).
- B9 mới: nguồn ảnh `soldier`, deadline W3d3, fallback escalate giảng viên (7 class).
- Fine-tune multi-GPU (`device=0,1`, batch tăng, epochs giảm ~30) + pin version ultralytics/torch vào repo.
- Field test location OK — không thay đổi phase-05.

**Verification Results (codebase claims):** 16 claims checked, 16 verified, 0 failed
(`tactical_slm.py:31,35-42,53,56-57,94` · `tactical_telemetry_feed.py:23,31,79-80` ·
`heretic_phase4_hud.py:29,60,80,184,193-195,204` · `tactical_hud_renderer.py:55,129`).

**Action items → phase impact:**
- plan.md: W1 (code-only, 360P tổng hợp), W3 (B9), W5 (sim-first), B1–B3 deadline, B6, B8→B9, KPI AC7, dependencies, open questions.
- phase-01: W1d5 → 360P tổng hợp; B1–B3 khi UAV về.
- phase-02: 8 class mới, mapping `military_vehicle`, B9, multi-GPU, pin version.
- phase-03: sim-first, variant chốt khi UAV về.
- phase-04: variant B (bay tay theo route) build trước; variant A (MAVLink) chỉ nếu B2=yes.

### Session 2 — 2026-10-16 (feedback giảng viên sau buổi trình bày)

**Feedback (tóm):** dataset phải rõ số đối tượng + cụ thể gì; **dataset thu từ UAV**
(độ cao, tốc độ, tham số — đặc thù UAV); nhiều object → cảnh báo cái **gần nhất**;
**ngưỡng khoảng cách** → cảnh báo người bảo vệ; người được bảo vệ gửi **vị trí liên tục**
để xác định hướng; target **trong tầm nhìn UAV** không; **UAV bay theo đối tượng**
(tóm lại: bay trên đầu → đi cùng → đo khoảng cách m + hướng → cảnh báo).

**Đã có sẵn (verify code, không sửa):** target gần nhất — `tactical_slm.py:104`
(`closest = min(alerting, key=distance)`); ngưỡng 100m/−10m/−1m — `tactical_slm.py:48`;
vị trí lính 1Hz → `distance_m` + `bearing` — `heretic_phase4_hud.py:61-72`;
câu SLM đã có khoảng cách + hướng (SYSTEM_PROMPT example).

**Decisions mới:**
- **Dataset góc UAV**: thêm **VisDrone** (ảnh drone: person, car, motorcycle, truck, bus)
  làm nguồn chính; MVRSD verify tham số thu (độ cao) từ dataset card; footage UAV thật
  tự quay (độ cao 30–50m, 3–5 m/s) = gold standard + nguồn `soldier` (B9);
  **tham số thu ghi vào báo cáo đồ án** (AC7).
- **Follow mode UAV** (Phase 4): sim = bay theo vị trí target (smoothing centroid track);
  real = MAVLink GOTO (variant A) / HUD chỉ hướng + khoảng cách cho phi công (variant B).
- **FOV indicator** (Phase 4): `point_in_cone(target_xy, cone)` → badge
  "MỤC TIÊU TRONG/NGOÀI TẦM NHÌN".
- Kịch bản demo §7 PDR: thêm step follow + câu cảnh báo có m + hướng.

**Impact:** PDR (S1/S4/S5, bảng dataset 8 class, AC3/AC6/AC7, §7, rủi ro VisDrone) ·
plan.md (W3/W4/W7, KPI) · phase-02 (VisDrone + tham số thu) · phase-04 (follow + FOV
indicator) · supervisor-briefing (mục trả lời feedback).
