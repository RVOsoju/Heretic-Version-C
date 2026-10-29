# Dataset — tham số thu & nguồn (báo cáo đồ án)

Bảng tổng hợp 4 nguồn hợp nhất thành `heretic-8c` (33,221 ảnh, 8 class) +
tham số thu cho phần "dataset đặc thù UAV" (yêu cầu giảng viên 2026-10-16, AC7).
Cập nhật 2026-10-29.

## 1. Bảng 4 nguồn

| Nguồn | Platform | Độ cao | Tốc độ | FOV | Resolution (đo mẫu) | Ảnh (merge) | Class đóng góp | License |
|-------|----------|--------|--------|-----|--------------------|-------------|----------------|---------|
| **VisDrone** | Drone (AISKYEYE, Tianjin U) — urban/suburban China | biến đổi, card không ghi số cố định | — | — | 1360×765 | 9,209 | person, car, motorcycle, truck, bus | CC BY-NC-SA 3.0 |
| **MVRSD** | Aerial (drone/satellite) | card không ghi số cố định | — | — | 640×640 | 13,582 | military_vehicle | (xem card nguồn) |
| **Mendeley** | UAV bird's-eye | card ghi "altitude variation", không số cố định | — | — | 640×640 | 7,985 | soldier, military_vehicle, person | CC BY 4.0 |
| **COCO boat** | **Ground/street-level — KHÔNG phải UAV** | — | — | — | 640×480 (biến đổi) | 3,025 | boat | CC BY 4.0 |

**Ghi chú trung thực (để trình bày với giảng viên):**
- 3/4 nguồn là góc **aerial/UAV** (VisDrone, MVRSD, Mendeley) — đúng "dataset thu từ UAV".
- **COCO boat là nguồn ground-level duy nhất** (boat to, gần, cảnh harbor/street). Dùng vì
  boat không có trong 3 nguồn UAV. Domain gap boat (UAV nhìn xuống → boat nhỏ) đã ghi nhận,
  chấp nhận vì boat là class phụ (cảnh báo), không phải class chính.
- Độ cao/tốc độ/FOV của 3 nguồn UAV **không có số cố định** trong dataset card — ghi trung
  thực như vậy, không bịa số. Số cố định chỉ có ở footage tự quay (mục 3).

## 2. Số lượng object theo class (AC7: "rõ số đối tượng + cụ thể gì")

| Class | # box | Nguồn chính |
|-------|-------|-------------|
| car | 187,005 | VisDrone |
| person | 153,583 | VisDrone + Mendeley |
| motorcycle | 40,378 | VisDrone |
| military_vehicle | 32,172 | MVRSD + Mendeley |
| boat | 10,576 | COCO |
| truck | 16,284 | VisDrone |
| bus | 9,117 | VisDrone |
| soldier | 3,437 | Mendeley |
| **Tổng** | **452,552 box / 33,221 ảnh** | |

**Mất cân bằng:** car 187k : soldier 3.4k ≈ 54:1 — ghi nhận, strategy = train as-is rồi đọc
per-class mAP, iterate (oversample soldier / tăng epochs) nếu soldier yếu. Backup: Roboflow
~4.8k soldier (cần token, deferred) → soldier ~8k nếu cần.

## 3. Footage tự quay (i1 Pro / Mini 2 SE) — SẼ BỔ SUNG khi đi quay

Nguồn gold-standard, góc UAV thật, **có tham số cố định** (khác 4 nguồn public trên).
Mỗi lần thu ghi vào log:

| Lần | Ngày | UAV | Độ cao (m) | Tốc độ (m/s) | Tilt/gimbal (°) | FOV (°) | Res | Khoảng cách target (m) | Ghi chú |
|-----|------|-----|-----------|-------------|-----------------|---------|-----|------------------------|---------|
| 1   |      |     |           |             |                 |         |     |                        |         |

Nominal plan: **độ cao 30–50m, tốc độ 3–5 m/s, FOV ~60°** — log thật confirm/sửa số này.
FOV phải **đo** (B1: bay 30m, đánh dấu 2 điểm cách 10m, đếm pixel).

## 4. License summary

- VisDrone **CC BY-NC-SA 3.0** (NC = non-commercial) — phù hợp đồ án học thuật, không thương mại.
- Mendeley, COCO: **CC BY 4.0** (gồm cả thương mại).
- MVRSD: theo card nguồn (mirror InvictusRex) — verify khi cite.
