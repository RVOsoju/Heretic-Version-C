# PM Progress Review — 18/11 (W5d3)

**Plan:** `plans/261015-1637-phase5-3-month-roadmap/` · Tổng: **W1–W4 ✓ (M1 + M2 done), W5 chưa bắt đầu**

## Đã xong (có bằng chứng)

| Tuần | Kết quả | Bằng chứng |
|------|---------|------------|
| W1 ✓ 19/10 | ByteTrack + TrackStore + gater track_id; 360P P 0.74/R 0.79 | `test_tracking.py`, `test_360p_precision.py` |
| W2 ✓ 26/10 | Height anchor + flash AC4 + AC1 (re-ID 0.0%) + AC2 (1.2%) + AC3 → **M1** | `test_tracking.py` 7/7, `test_telemetry_chain.py` 20/20 |
| W3 ✓ sớm 27–29/10 | heretic-8c 33,221 ảnh 8 class (MVRSD+VisDrone+Mendeley+COCO boat) | `prepare_heretic_8c_dataset.py`, yaml |
| W4 ✓ sớm 30/10–04/11 | 26s-rebal mAP50 **0.6314** (soldier 0.895, mil_vehicle 0.957); K2 clip: soldier 2,236 det + tank; SLM 8c + `--model`; K2 finetune 11/10 | `weekly-261104-w4-report.md`, `weights/yolo26s-military-8c*.pt` |
| Ngoài plan 11/16–18 | TensorRT export script · minimap heading-up + `--heading` + mũi tên N | `export_trt_engine.py`, plan 261116-1156 |

## Còn lại (theo plan)

| Tuần | Ngày | Việc | Trạng thái |
|------|------|------|------------|
| **W5** | 16/11–22/11 | Bench 2 node + WireGuard + `udp_position_sender.py` + `test_vpn_link.py` (AC5) | **CHƯA BẮT ĐẦU (tuần hiện tại)** |
| W6 | 23/11–29/11 | `--source` webcam/rtsp/uvc/file + tune 360P (nửa AC8) | Chưa |
| W7 | 30/11–06/12 | Badge FOV (cone visual đã bỏ 11/16) + patrol + follow + tam giác phân GPS (AC6) | Chưa |
| W8 | 07/12–13/12 | Tích hợp full 3 chế độ degradation (M4) | Chưa |
| W9 | 14/12–20/12 | Field test Mini 2 SE — 5 kịch bản | **BLOCK: Mini 2 SE chưa mua** |
| W10 | 21/12–27/12 | Stress VRAM/link/latency (AC9) | Chưa |
| W11 | 28/12–03/01 | Demo E2E 10 phút (AC11) | Chưa |
| W12 | 04/01–10/01 | Docs + báo cáo đồ án + buffer | Chưa |

## Rủi ro / việc cần người dùng

1. **Mini 2 SE chưa mua** — gate B1–B3 + W9; cần về tay **trước 14/12** (~4 tuần).
2. **GY-85 (la bàn)** — user mua; phía code đã sẵn (`--heading`).
3. **Laptop (việc user):** verify realtime FPS 26s-k2-cp @4GB · build TensorRT engine · (W4d4 carry).
4. **Retrain 26n 100ep (16/11) mất dấu** — không process, không weight, không log sau epoch 1 → cần xác nhận có cần chạy lại không (26n chỉ là fallback; weight demo = 26s-k2-cp).
5. **False positive tarp→boat/soldier/mil-vehicle** — domain gap; fix = hard-negative mining (chưa làm).
6. **bus↔boat lẫn @360p** — known issue.
7. **mAP50 gate 0.75 miss (0.631)** — đã chấp nhận có lý do; nếu giảng viên ép: thêm data truck/motorcycle/boat + imgsz 800.

## Sync-back đã làm
- `plan.md`: W4 ✓ + Phase 2 → Done + ghi chú W7 (cone bỏ) + mục "Ngoài plan 11/16–18".
- `phase-02`: status → completed + success criteria đánh dấu theo số đo thực.

## Unresolved questions
- Retr 26n 100ep (16/11): chạy lại không, hay bỏ (26s là weight demo)?
- W5: node 2 dùng máy nào (laptop 2 / điện thoại Termux)?
