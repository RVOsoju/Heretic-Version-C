---
title: TensorRT FPS + Minimap radar upgrade
status: completed
priority: P1
effort: medium
branch: main
tags: [tensorrt, minimap, radar, hud]
created: 2026-11-16
---

# TensorRT + Minimap radar

2 mục, đều đã chốt phương hướng với user:

## Mục 1 — TensorRT (tăng FPS, giữ ByteTrack)
- **Ràng buộc then chốt:** `.engine` ghim theo kiến trúc GPU + phiên bản TRT.
  Engine build trên server (Ada 8.9) **KHÔNG chạy** trên laptop 3050 (Ampere 8.6).
  → TensorRT là thao tác **phía laptop**. Server KHÔNG cài TRT (download nặng,
  rủi ro lệch version, engine không port được).
- `heretic_phase4_hud.py`: `--model` đã nhận `.engine` (ultralytics `YOLO("x.engine")`
  load trong suốt). ByteTrack giữ nguyên (`tracker="bytetrack.yaml"` là post-inference,
  độc lập backend). Chỉ cập nhật help text.
- Tạo `export_trt_engine.py` (~40 dòng): `.pt` → `.engine` (half, imgsz, device).
  Chạy TRÊN LAPTOP. Doc: `docs/laptop-deployment-guide.md` thêm section TensorRT.
- **Không test engine trên server** (chưa có TRT). Validate: script parse OK,
  đường dẫn không-engine (`--sim`) vẫn chạy.

## Mục 2 — Minimap radar
Minimap hiện đã theo hướng radar (tâm = lính, chấm địch theo hướng+khoảng cách).
Nâng cấp thành radar hoàn chỉnh, **giữ bán kính 100m** (`WARN_RANGE_M`):
1. **Range ring** 25/50/100m + nhãn.
2. **Cone FOV camera** (góc ngang ~70°) — vùng camera đang nhìn (đạt AC6).
3. **Góc thật 0-360°** thay 4 phương: `calculate_tactical_telemetry` trả thêm
   `angle_deg`; đặt chấm bằng `ex=cx+r·cos(a)`, `ey=cy-r·sin(a)` (lên màn hình = "Bắc").
4. **Indicator trong/ngoài tầm nhìn**: target ngoài cone FOV vẽ rỗng (ghosted).
5. Mũi tên hướng camera (lên = phía trước).

Giữ chuỗi `bearing` 4 phương cho text cảnh báo + nhãn bbox (dễ đọc). Chỉ map dùng góc thật.

## Todo
- [x] `tactical_hud_renderer.py`: `math`, `CAM_FOV_DEG`, `_cone_points`, `_in_fov`,
      thay `BEARING_VEC`→`BEARING_ANGLE`, viết lại `draw_minimap`, update `render_hud`.
- [x] `heretic_phase4_hud.py`: `calculate_tactical_telemetry` trả 3 giá trị,
      `build_tactical_data` thêm `angle_deg`, sim loop thêm `angle_deg`, help `--model`.
- [x] `export_trt_engine.py` mới.
- [x] `docs/laptop-deployment-guide.md`: section TensorRT.
- [x] Test: `py_compile` 3 file + `--sim` render radar (xác nhận radar: cone+rings+ghosting).
- [x] Test: `test_telemetry_chain.py` + `test_tracking.py` → TOÀN BỘ PASS (không regression).
- [x] Code-review (subagent) — CLEAN, production-ready, 0 blocking issues.

## Success
- `--sim` ra PNG radar: ring + cone FOV + chấm góc thật + UAV + lính, không lỗi.
- `test_telemetry_chain.py` / `test_tracking.py` không regression (đường cảnh báo ổn).
- `export_trt_engine.py --help` chạy OK (engine build chạy trên laptop, không test server).
