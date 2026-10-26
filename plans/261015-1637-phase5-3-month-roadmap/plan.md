---
title: "Heretic C Phase 5 - 3-month roadmap (no budget, WiFi/4G VPN, 360P UAV)"
description: "Lộ trình 12 tuần cho đồ án Heretic C: tracking + YOLO 8 class + mạng riêng VPN + UAV 360P + demo E2E, ngân sách 0 đồng mua mới."
status: in-progress
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
chỉ dùng laptop TUF F15 (runtime), server 4× RTX 5000 Ada (fine-tune), UAV demo:
**i1 Pro** (mini drone 360–480P, WiFi → app phone — chim tập, đã có tay 23/10) +
**DJI Mini 2 SE** (249g, GPS + áp kế + gimbal 1080P — demo chính, user mua riêng, chưa có).
Mỗi tuần có 1 deliverable đo được; mọi điểm mù được ghi nhận và có deadline giải quyết.
Nguồn scope: `docs/project-overview-pdr.md` (S1–S7, AC1–AC11).

**Giới hạn cứng (quyết định 2026-10-15):** không LoRa, không E88 Pro, không haptic (AC4 fallback = flash HUD + SLM),
không thermal. TelemetryFeed interface (UDP 8888, JSON `{id,lat,lon,t}`) giữ nguyên
(+ trường `alt` optional từ W7 cho tam giác phân GPS — feed không đổi).

## 12-week roadmap

| Tuần | Ngày | Deliverable | Verify |
|------|------|-------------|--------|
| **W1 ✓** | 19/10–25/10 | **✓ DONE 19/10 (W1d1–d5):** baseline 11/11 + 16 khung; ByteTrack (`model.track`, bytetrack.yaml) + `TrackStore` (velocity/approach/prune) + gater re-key `track_id` (fallback cũ) + `test_360p_precision.py` (360P tổng hợp) | ✓ `boxes.id` ổn định 30 khung (0 re-ID), overhead **1.5ms <5ms**; precision 360P **P 0.74/R 0.79** → B6 |
| **W2 ✓** | 26/10–01/11 | **✓ DONE 26/10 (W2d1–d5):** object-height anchor (`tactical_height_anchor.py` — scale/class + fallback 0.05, `make_sim_frame` vật lý 30m/FOV60°) + flash HUD (3 khung @30fps, không âm) + `test_tracking.py` (150 khung, YOLO26n + ByteTrack thật) + AC3 vào `test_telemetry_chain.py` → **M1 done** | ✓ AC1: 150/150 khung, re-ID **0.0%** · AC2: 2.32 vs 2.29 m/s (**sai 1.2%**) · anchor 1.2–1.3% (<25%) · AC3: 105→95m cùng track = 1 cảnh báo, 3 target → chọn 42m · AC4: flash ≈100ms · 20/20 + 7/7 checks PASS |
| **W3** | 02/11–08/11 | Tải MVRSD (verify Baidu; fallback AMAD/InvictusRex) + **VisDrone** (góc drone: person + 4 xe); **verify tham số thu** (độ cao/tốc độ/FOV) từ dataset card; prep data, map 8 class; **research nguồn `soldier`** (B9 — ưu tiên footage UAV tự quay) | `mvrsd-8c.yaml` hợp lệ, 3000 ảnh trên server; VisDrone subset 5 class; **tham số thu UAV ghi vào report**; B9 có kết quả |
| **W4** | 09/11–15/11 | Fine-tune yolo26n → 8 class (MVRSD + **VisDrone** + `soldier` + COCO regression) + regression check → **M2 done** | `yolo val` mAP50 ≥0.75 (val MVRSD+VisDrone); mAP 6 class COCO giảm ≤5 điểm; tham số thu UAV ghi báo cáo (AC7) |
| **W5** | 16/11–22/11 | **Sim-first**: dựng bench 2 node (laptop + node 2) + WireGuard, `udp_position_sender.py` — không phụ thuộc UAV | `wg show` 2 peer active; ping <20ms; `test_vpn_link.py` PASS (AC5 phần bench) |
| **W6** | 23/11–29/11 | Video source abstraction (`--source webcam/rtsp/uvc/file`); hiệu chỉnh YOLO cho 360P → **M3 done** | ≥15fps @360P; người trong khung → cảnh báo <2s (nửa AC8) |
| **W7** | 30/11–06/12 | Cone FOV trên minimap + **badge target trong/ngoài tầm nhìn** + tuần tra + **chế độ follow target** (MAVLink qua DJI Virtual Port nếu verify OK, nếu không = route gợi ý tay + HUD chỉ hướng) + **tam giác phân GPS** (`tactical_geolocation.py`: pose UAV + pixel → lat/lon target; `alt` vào payload UDP; đo FOV → B1) | `--sim` lộ trình waypoint: cone đúng hướng, **UAV bay theo vị trí mục tiêu**, **khoảng cách target→lính sai <15%** so ground truth (AC6 sim) |
| **W8** | 07/12–13/12 | Tích hợp full: telemetry qua VPN, 3 chế độ degradation (full/position-only/local), link-loss test → **M4 done** | AC6 (bay thật nếu được, nếu không sim+bench); AC8: 10 phút live ổn định; cắt link → local ≤5s không crash |
| **W9** | 14/12–20/12 | Field test 1 với UAV demo (Mini 2 SE; i1 Pro nếu chưa kịp) — 5 kịch bản, ghi log + video | Log: 5/5 kịch bản chạy, issue list đã triage (critical/minor) |
| **W10** | 21/12–27/12 | Stress: VRAM 4GB, link loss, latency + fix | AC9: <3.8GB/30s, OOM → `--cpu` khởi động lại OK; 5 vòng cắt/ghép link ≤5s |
| **W11** | 28/12–03/01 | Demo end-to-end 10 phút (kịch bản PDR §7) + 2 buổi rehearsal | AC11: 1 lượt chạy không interrupt, có ghi hình; re-verify AC1–AC11 |
| **W12** | 04/01–10/01 | Tài liệu đồ án (cập nhật `docs/`, báo cáo cuối) + buffer | `docs/` đồng bộ (deployment + VPN, PDR status, BOM status); báo cáo đồ án đủ bảng kết quả AC1–AC11 |

## Sơ đồ hệ thống

```
                    MẠNG RIÊNG (WiFi/4G) + WireGuard
  ┌────────────────────────────┐          ┌─────────────────────────────────────────────┐
  │  UAV DEMO                  │          │  LAPTOP C2 — TUF F15 (RTX 3050 4GB, Win11)  │
  │  i1 Pro (tập) / Mini 2 SE  │  video   │                                             │
  │  (demo: GPS + gimbal)      │          │  YOLO 8c + ByteTrack → TrackStore          │
  │  camera ───────────────────┼─────────►│    → gater (key = track_id) → câu cảnh báo │
  │   WiFi → app phone (DJI Fly)          │      (template 0ms; SLM qwen2.5 optional)  │
  │   → scrcp USB → laptop    │          │    → HUD OpenCV: box + minimap + cone FOV  │
  │                            │ position │  TelemetryFeed UDP :8888 (interface giữ    │
  │  GPS + alt + góc gimbal    │          │  nguyên, TTL 5s = STALE_AFTER_S)           │
  │  (Mini 2 SE) ──────────────┼─────────►│                                             │
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
| B1 | **alt + FOV thực của Mini 2 SE** (input tam giác phân GPS) — *downlink đã rõ 23/10: cả i1 Pro lẫn Mini 2 SE đều WiFi → app phone → scrcp USB → laptop* | Variant video W6 = phone-scrcp (chốt 23/10); geolocation W7 (nominal h=30m, FOV 60° tới đó) | **Khi Mini 2 SE về tay + 1 tuần** | **Đo FOV (bay 30m, đánh dấu 2 điểm cách 10m, đếm pixel) + verify alt + đọc góc gimbal app**; ghi kết quả vào đây; tới trước W9 (field test) |
| B2 | **MAVLink/GCS** — Mini 2 SE: **DJI Virtual Port** (MAVLink tập hợp giới hạn: telemetry + GOTO/waypoint) — verify thực | W7: upload waypoint tự động (variant A) vs bay tay theo route gợi ý (variant B — build trước) | **Khi Mini 2 SE về tay + 1 tuần** | DJI Assistant/virtual port + QGroundControl; i1 Pro: không MAVLink (chỉ chim tập) |
| B3 | **Vị trí UAV** — Mini 2 SE: **có GPS + áp kế** ✓ (spec 23/10); i1 Pro: không GPS (chỉ chim tập) | W7 tam giác phân GPS khả thi với Mini 2 SE | **Đóng khi Mini 2 SE về tay** (verify GPS lock + alt) | i1 Pro không block gì (chỉ tập bay + test scrcp bridge) |
| B4 | Node ESP32+NEO-6M trong BOM **chưa mua** (`hardware-bom.md` ghi "chưa mua") | Không có node GPS vật lý → demo dùng `--soldier-gps` + đồng đội mô phỏng | W1 | Đếm kho; nếu không có → dùng đường sim (code đã hỗ trợ) |
| B5 | **MVRSD qua Baidu pan** — server có truy cập không? | Trễ 1 tuần W3 → W4 trôi | W3 (ngày 1) | Test tải 1 file trên server; fallback AMAD / InvictusRex (GitHub release) |
| B6 | **Chất lượng 360P** (người 20m ≈ 40–60px) | Detection rớt → phải tune imgsz/NMS ở W6 | W1 (video tổng hợp); retest frame thật khi UAV về | **W1d5 ✓ (19/10):** `test_360p_precision.py` — 30 frame 640×360 (bus.jpg pan): **P 0.74 / R 0.79** (conf ≥0.25, person ~170px) — người to; khi bay thật (i1 Pro / Mini 2 SE) retest frame thật (người 16–40px) mới là dữ liệu quyết định |
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
| 1 | [Tracking and gater track_id](./phase-01-tracking-and-gater-track-id.md) | **Done** (W1 ✓ 19/10, W2 ✓ 26/10 — AC1–AC4 + anchor; còn item UAV về tay trước W9 = B1–B3) |
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
- **Ngoại bộ:** UAV demo — i1 Pro **đã có tay 23/10 (chim tập)**; Mini 2 SE **chưa có** (user mua riêng) — gate B1–B3 còn lại (đo FOV/alt + verify DJI Virtual Port) khi Mini 2 SE về tay; chỉ block khối W5–W8 (bay thật W8/W9), **W1–W4 không bị block** (sim-first); quyền truy cập Baidu (gate B5, khối W4); nguồn ảnh `soldier` (gate B9, khối W4 train).

## Open questions

1. **Downlink video** — ĐÃ RÕ (23/10): i1 Pro + Mini 2 SE đều **WiFi → app phone** (DJI Fly) → bridge **scrcp USB → laptop** (variant video W6 chốt). UAV "được cấp" (nếu về) vẫn là lựa chọn thay thế.
2. **DJI Virtual Port** (Mini 2 SE) có GOTO/waypoint ổn định không (tuần tra tự động)? → verify khi nhận máy → variant A/B tuần tra W7.
3. Có sẵn **SIM 4G/data** nào không? → nếu không: chỉ WiFi riêng (demo trong vùng phủ AP).
4. Module rung (haptic) có được cấp thêm sau này không? → giữ blocked; AC4 fallback flash + SLM.
5. **Nguồn ảnh class `soldier`** (B9) — dataset mở hay tự ghi footage thao trường? → research W3, chốt trước train W4.
6. Alt + góc gimbal — Mini 2 SE: **có áp kế + đọc góc gimbal trong app** ✓ (23/10) → input tam giác phân GPS (W7); verify số liệu thực khi nhận máy.

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

### Session 3 — 2026-10-16 (hình học bay vòng + model khoảng cách)

**Câu hỏi (user):** UAV bay vòng quanh lính (không trên đầu) thì tính khoảng cách
target→lính thế nào? (User nhớ code đang ánh xạ qua độ cao + góc chúi + pixel.)
**Verify:** `heretic_phase4_hud.py:29,41-57` — code hiện tại là model pixel-scale phẳng
(`PIXEL_TO_METER = 0.05`, tâm ảnh = lính), **không có** alt/tilt → đúng chỉ khi UAV
thẳng trên đầu; bay vòng → sai có hệ thống.
**Decisions (user chốt):** tam giác phân GPS (GPS UAV + alt + góc chúi + FOV + pixel →
lat/lon target → 2D tới lính, ±10–15%) đặt **Phase 4 (W7)**; Phase 1 không đổi (gater
model-agnostic, vẫn nhận `distance_m`); bay vòng (bán kính 60–80m) + follow tách tầm
phát hiện (xuyến 30–40m trên 360P) khỏi tầm đo (GPS) → ngưỡng 100m giữ nguyên.
**Impact:** phase-04 (tactical_geolocation.py, `alt` payload, đo FOV/alt → B1, success
criteria +1, risk +1) · PDR (header, S1, Scope OUT, AC2, §7 step 5, rủi ro, open Q6) ·
plan.md (W7, B1, open Q6) · supervisor-briefing (header, §3 Q&A mới, §4 điểm trung thực).

### Session 4 — 2026-10-16 (object-height anchor — cầu nối W2)

**Câu hỏi (user):** pixel distance có khó khăn gì, cách nào tốt hơn? Hướng tiếp cận
xác định thế nào?
**Verify:** `PIXEL_TO_METER = 0.05` hiệu chuẩn cho footprint 32×18m → độ cao ~15–22m;
ở độ cao bay plan 30–50m scale thật 0.064–0.16 → **sai hệ thống ×1.5–3** (cảnh báo
100m trigger thực ở ~35–70m). Bearing hiện tại: atan2 4 hướng, giả định cạnh trên ảnh
= Bắc → sai khi UAV quay đầu.
**Decisions (user chốt):** thêm **object-height anchor vào Phase 1 (W2)** — scale =
kích thước thật class / chiều cao box (bảng `CLASS_HEIGHT_M`), fallback 0.05 khi
`box_h < 8px`; ±15–25%, không cần phần cứng, giảm nhẹ B1. W7 (tam giác phân GPS) vẫn
là model chính. Hướng tiếp cận W7: bearing = atan2(GPS target − GPS lính) (la bàn thật,
không phụ thuộc camera) + "đang tiếp cận" = dR/dt < 0 từ velocity track.
**Impact:** phase-01 (overview, requirements, architecture, W2d1 mới, success +1, risk +1) ·
PDR (header, S1, Scope OUT, AC2, rủi ro) · plan.md (W2) · supervisor-briefing (§3, §4).

### Session 5 — 2026-10-16 (review toàn bộ trước khi bắt đầu W1)

**Scope:** plan.md + 5 phase files + PDR + briefing — consistency, AC coverage, ngày tuần,
interface, điểm start W1.
**Gap find + fix ngay:**
1. **AC4 (flash <100ms) không có bước implement ở phase nào, code không có `flash`**
   (grep verify) → đặt vào Phase 1 W2d2 (gater trigger → overlay ≤3 khung @30fps, không âm);
   phase-01 (overview/req/arch/files/steps/success) + plan.md W2 cập nhật.
2. `make_sim_frame` (`heretic_phase4_hud.py:108`) sinh khung theo constant 0.05 → không có
   ground truth vật lý để test height anchor → W2d1 thêm sub-step: sinh khung theo
   (h=30m, FOV 60°): `scale = 2h·tan(FOV/2)/360`, box người = 1.7/scale px.
3. Payload UDP: plan.md ghi "giữ nguyên `{id,lat,lon,t}`" nhưng phase-04 thêm `alt` (W7)
   → ghi rõ `alt` là trường **optional**, `TelemetryFeed` không đổi.
4. W1 thêm **baseline test suite đầu tuần** (11/11 + `--sim`) trước khi sửa code.
5. Briefing §6 M4: thiếu geolocation → bổ sung.
**OK (không đổi):** 8 class list đồng bộ 5 file · AC1–AC11 đều có phase + tuần (AC4 đã fix) ·
ngày W1–W12 khớp (W1 = T2 19/10) · dependencies P1–P5 đúng · B1–B9 có deadline ·
`TelemetryFeed`/gater interface không đổi · 200-line rule: phase-04 tách `tactical_uav_fov.py`/
`tactical_geolocation.py` sẵn.
**Còn mở (fix dần — có deadline trong register):** B1–B3 (UAV về, trước W9) · B5 (Baidu, W3d1) ·
B6 (360P, W1 + retest) · B7 (SIM 4G, W5) · B9 (ảnh soldier, W3d3) · alt/FOV thực (B1) ·
`military_vehicle` height 3.0m (verify W4).

### Session 6 — 2026-10-19 (W1 thực thi: W1d1–W1d5)

**Scope:** thực hiện W1 theo plan (code-only, UAV-agnostic).
**Đã làm:**
1. Cleanup: xóa `heretic_phase1.py` + `heretic_phase2.py` (prototype cũ 25/9); sửa docstring
   `tactical_slm.py` (tham khảo phase2 → pipeline).
2. Baseline đầu tuần: `test_telemetry_chain.py` **11/11 PASS** + `--sim` **16/16 khung**
   (Ollama 11434 CPU-only timeout trên dev server → khung "quiet" — môi trường, không phải lỗi).
3. **W1d1:** `heretic_phase4_hud.py` — `model()` → `model.track(persist=True,
   tracker="bytetrack.yaml")`; verify trên `assets/bus-360p.mp4` (30 khung): `boxes.id`
   ổn định, **0 re-ID** (3 person ids 1/2/12); overhead ByteTrack **1.5ms/khung <5ms**.
4. **W1d2:** `tactical_tracker.py` (mới, 66 dòng) — `TrackStore`: update/velocity/approach/
   prune, cửa sổ 5 khung, max_age 2s. `update` thêm tham số `scale` (velocity = Δpx/Δt×scale).
5. **W1d3:** `build_tactical_data` + `enemies_payload` thêm `track_id` + `approach_mps`
   (backward-compat: param optional, `.get()` trong payload).
6. **W1d4:** `tactical_slm.py` `_key()` ưu tiên `track_id`, fallback `(target, bearing)` —
   sim/demo không track không đổi hành vi.
7. **W1d5:** `test_360p_precision.py` (mới) — video 640×360 30 khung từ bus.jpg (pan);
   **P 0.74 / R 0.79** (conf ≥0.25) → log B6. assets/ thêm bus-720p-canvas.jpg + bus-360p.mp4.
**Verify:** tester 6/6 PASS 0 regression · code-reviewer a–e PASS, 0 BLOCKER/MAJOR,
5 MINOR (last_warned không prune — bounded, chấp nhận; file 234 dòng >200 — pre-existing;
GT circularity 360P — documented; assets/ nên commit).
**Còn mở W1 (cho W2):** `test_tracking.py` (AC1/AC2), object-height anchor (AC2/AC3),
flash HUD (AC4), AC3 gater 100m, B4 (đếm kho node ESP32 — việc vật lý của user).

### Session 7 — 2026-10-19 (quyết định: kênh câu chữ = template chính + SLM optional)

**Câu hỏi (user):** "LLM vai trò quá mờ nhạt — nên loại bỏ, cảnh báo/logic/tính toán
đặt ở back-end, sẽ nhẹ hơn."
**Verify:** đúng một phần — logic đã 100% ở back-end (gater, distance, closest, flash);
SLM chỉ render payload → câu tiếng Việt. Chi phí thật: ~2GB/4GB VRAM + 0,4–1,5s + phụ
thuộc Ollama (timeout 10s khi down).
**Decision (user chốt: hybrid):** template f-string = kênh chính (0ms, 0 VRAM, luôn hoạt
động, `template_alert()` trong `tactical_slm.py`); SLM = optional qua `--slm`
(warmup + call chỉ khi bật; Ollama down → fallback template). `DANGEROUS_TARGETS` +
`soldier, military_vehicle` (forward-compat 8 class W4). `--sim` giờ 2,6s (trước ~2,5 phút)
và ra khung `*_alert.png` có câu chữ.
**Lý do không bỏ hẳn:** "câu chữ AI" là 1 trong 3 kênh của PDR + story đồ án + đã trình
giảng viên; hybrid giữ story mà hệ robust hơn. Quantization: qwen2.5:3b Ollama đã là
Q4_K_M (~2GB) — sweet spot, không đổi.
**Impact:** `tactical_slm.py` (template_alert, evaluate_alert(use_slm), --slm) ·
`heretic_phase4_hud.py` (--slm, warmup có điều kiện) · `test_telemetry_chain.py` (+3
checks = 14) · PDR (header, §1, S1, S7, AC10, §7, risks) · briefing (header, §1, §4, §5) ·
plan.md (architecture).

### Session 8 — 2026-10-23 (UAV demo chốt: i1 Pro + Mini 2 SE, W7 giữ nguyên)

**Bối cảnh:** UAV "được cấp" chưa rõ ngày về; user mua **i1 Pro** (Shopee, mini drone
360–480P, WiFi → app phone 50–100m, 2.4GHz, pin 10–15 phút, không GPS, không MAVLink).
**Decision (user chốt):** (1) **i1 Pro = chim tập** (rèn phi công + test scrcp bridge);
(2) **chờ DJI Mini 2 SE làm UAV demo chính** (249g, GPS + áp kế + gimbal 1080P, bay 31 phút,
user mua riêng ~7–9tr) — **W7 tam giác phân GPS giữ nguyên** (user không muốn bỏ W7);
(3) downlink cả 2 drone = **WiFi → app phone → scrcp USB → laptop** → **variant video W6 chốt**
(loại RTSP/FPV 5.8G); (4) S4: Mini 2 SE có **DJI Virtual Port** (MAVLink giới hạn:
GOTO/waypoint) → patrol/follow mode đầy đủ, verify khi nhận máy; i1 Pro không MAVLink.
**Impact:** plan.md (overview, sơ đồ, W7/W9, B1–B3, B6, dependencies, open Q1/Q2/Q6) ·
PDR (header, giả định, S4, S6, AC8, risks, open Q1/Q2/Q6) · briefing (header, §1, §6, §7, §8).
**Còn mở:** ngày mua Mini 2 SE (cần về trước W9); đo FOV/alt + verify virtual port (B1/B2
khi nhận máy); 5 câu spec i1 Pro (GPS/app/tilt/trần bay/pin) — giảm độ ưu tiên vì chỉ chim tập.

### Session 9 — 2026-10-26 (W2 done: object-height anchor + flash AC4 + test_tracking AC1/AC2/AC3 → M1 done)

**Bối cảnh:** đầu W2 (26/10) — user: "xong W2 đã, nếu chiều chưa xong thì song song W3".
**Verify (đo thật, không mock):**
- **W2d1 anchor:** `tactical_height_anchor.py` — scale = kích thước class / box_h, fallback
  0.05 (class thiếu hoặc box_h <8px); `make_sim_frame` vật lý 30m/FOV60° (scale 0.02706 m/px,
  người 62px). Frame tổng hợp 15m/10m → anchor sai **1.2–1.3%** (ngưỡng <25%; constant 0.05
  cũ sai ×1.92 trên cùng frame).
- **AC4 flash:** `render_hud(flash=)` overlay đỏ toàn màn, 3 khung @30fps ≈ 100ms, không API
  âm thanh (grep verify). `sim_hud_90m_quiet.png` đỏ = frame 2/3 decay sau alert 95m.
- **AC1/AC2 (`test_tracking.py` mới):** 150 khung 30fps, person 62px (crop bus.jpg) đi
  1100→680px, YOLO26n + ByteTrack thật @imgsz=1280 → detection **150/150**, re-ID **0.0%**,
  approach **2.32 vs gt 2.29 m/s (sai 1.2%)**.
- **AC3 (`test_telemetry_chain.py` +6 checks = 20):** 105m→95m cùng track_id = đúng 1 cảnh
  báo, 95m lặp = im lặng; 3 target 95/42/60m → chọn **42m**.
- `--sim` 16/16 khung, gater nhịp 10m/1m đúng.
**Issues fix sau code-review (0 BLOCKER/MAJOR, 3 MINOR):** `full_track_approach` đọc cục bộ
`detections` thay vì `store.tracks` (cửa sổ 5 khung — tên không đúng nội dung); bỏ check
tautological `3/30 <= 0.1`; strip tham chiếu plan (W2/AC4) khỏi comment code (test giữ AC
cho traceability).
**Impact:** `tactical_height_anchor.py` (mới) · `heretic_phase4_hud.py` (per-box anchor,
sim vật lý, flash) · `tactical_hud_renderer.py` (flash param) · `test_tracking.py` (mới,
7 checks) · `test_telemetry_chain.py` (20 checks) · phase-01 **completed** · plan.md W2 ✓.
**Còn mở W3 (02/11):** MVRSD (test Baidu = B5) + VisDrone download trên server; W4 gate
mAP50 ≥0.75 → 26s fallback (26l loại — VRAM 4GB).
