---
phase: 2
title: "YOLO 8-class fine-tune MVRSD trên server (M2)"
status: pending
priority: P1
effort: "2w"
dependencies: []
---

# Phase 2: YOLO 8-class fine-tune MVRSD (M2)

## Overview

W3–W4, chạy trên server 4× RTX 5000 Ada (laptop không train): tải MVRSD (~3000 ảnh) +
**VisDrone** (ảnh drone: person + 4 xe), prep data, fine-tune yolo26n từ 6 class COCO
lên 8 class (`person, soldier, car, motorcycle, truck, bus, boat, military_vehicle` —
chốt 2026-10-15), verify AC7 (mAP50 ≥0.75 trên val, mAP 6 class COCO giảm ≤5 điểm).
Dataset **đặc thù góc UAV** (yêu cầu giảng viên 2026-10-16): tham số thu
(độ cao/tốc độ/FOV) verify từ dataset card + ghi vào báo cáo đồ án.
**Độc lập với Phase 1** — chạy song song, không đụng file nào của Phase 1.

## Requirements

**Functional**
- 8 class (chốt 2026-10-15): `person, soldier, car, motorcycle, truck, bus, boat, military_vehicle`
  — **gộp tất cả xe quân sự thành 1 class** (không phân tank/IFV/pháo), **loại máy bay**,
  **phân biệt người thường (`person`) / lính (`soldier`)**.
- `DANGEROUS_TARGETS` (`tactical_slm.py:31`): bỏ `person`, thêm `soldier` + `military_vehicle`,
  giữ 5 xe thường (`car, motorcycle, truck, bus, boat`).
- Nguồn ảnh class `soldier` (B9): **footage UAV thật tự quay (ưu tiên)** / dataset mở —
  chốt W3d3; không có nguồn → escalate giảng viên (giữ 7 class).
- **Đặc thù UAV** (yêu cầu giảng viên 2026-10-16): nguồn chính thu từ UAV — **VisDrone**
  (person, car, motorcycle, truck, bus) + MVRSD (drone/satellite) + footage UAV thật
  tự quay (khi UAV về). **Tham số thu** (độ cao 30–50m, tốc độ 3–5 m/s, FOV camera)
  verify từ dataset card + ghi vào báo cáo đồ án.
- Weight file mới chạy được trên laptop (RTX 3050 4GB), fps không giảm so yolo26n gốc
  (cùng kiến trúc "n"); **pin version ultralytics + torch (server == laptop)**.
- SLM nhận diện class mới: `SYSTEM_PROMPT` — soldier → "kẻ địch", military_vehicle →
  "xe quân sự địch", person → "dân thường" (không cảnh báo).

**Non-functional**
- Train chỉ trên server (`CUDA_VISIBLE_DEVICES` cố định, chạy overnight).
- Config train + dataset yaml commit vào repo (reproducible).
- Weight <~20MB (kích cỡ "n") — copy sang laptop qua USB/network.

## Architecture

Data flow (thực tế 28–29/10 — 4 nguồn đã merge):

```
4 nguồn (đều YOLO .txt) — đã tải + verify:
  - MVRSD     13,582 ảnh (mirror InvictusRex, Baidu không cần — B5 đóng)  → military_vehicle
  - VisDrone   9,209 ảnh (HuggingFace)                                    → person, car, motorcycle, truck, bus
  - Mendeley   7,985 ảnh (CC BY 4.0, fix 782 newline)                     → soldier, military_vehicle, person
  - COCO boat  3,025 ảnh (cat_id 9, prepare_coco_boat_subset.py)          → boat
  → prepare_heretic_8c_dataset.py: merge + remap class → dataset/heretic-8c/
      33,221 ảnh (train 26,691/val 3,343/test 3,187), 8 class, heretic-8c.yaml
  → train_military_yolo.py (server): train imgsz=640, epochs=30, batch=64,
      device=0,1 (multi-GPU — quyết định 2026-10-15)
  → weights/yolo26n-military-8c.pt
  → requirements-lock.txt: pin ultralytics + torch + torchvision (server == laptop)
  → laptop: heretic_phase4_hud.py --model weights/yolo26n-military-8c.pt
  → tactical_slm.py: DANGEROUS_TARGETS − "person" + {"soldier","military_vehicle"},
    SYSTEM_PROMPT: soldier → "kẻ địch", military_vehicle → "xe quân sự địch",
    person → "dân thường" (không cảnh báo)
```

Regression check (AC7 "mAP 6 class COCO giảm ≤5 điểm"): val model cũ (yolo26n gốc) + model
mới trên **coco128** (ultralytics tự download khi val) → chênh mAP50 ≤5 điểm. Không cần
tự build COCO 6-class subset — coco128 đủ cho check này.

**Logistics server (chốt 29/10 — hướng a):** `dataset/` gitignored → clone repo trên server
KHÔNG có dataset. **Chuyển 4 nguồn (~7.3GB) qua tarball** `dataset/heretic-8c-sources-for-server.tar`
(MVRSD + VisDrone + Mendeley + coco-boat-subset build sẵn — KHÔNG cần COCO zip 19G), extract
trên server, rồi **chỉ chạy `prepare_heretic_8c_dataset.py`** (rebuild heretic-8c, symlink trỏ
nguồn local). Bỏ qua `prepare_coco_boat_subset.py` trên server. Không transfer `heretic-8c`
merge trực tiếp vì symlink tuyệt đối bẻ gẫy + dereference ra cùng ~7.3GB mà mất nguồn gốc.
Giữ nguồn trên server để sau này re-merge Roboflow soldier / sửa class map.

## Related Code Files

**Create** (trạng thái 29/10 — dataset đã build, script train đã sẵn):
- `prepare_heretic_8c_dataset.py` (root) — **✓ XONG 28/10**: merge 4 nguồn (MVRSD + VisDrone +
  Mendeley + COCO boat) → `dataset/heretic-8c/{train,val,test}` + `heretic-8c.yaml`
  (33,221 ảnh, 8 class, symlink ảnh + label remap). Re-run an toàn.
- `prepare_coco_boat_subset.py` (root) — **✓ XONG 28/10**: extract 3,025 ảnh boat từ
  COCO 2017 (cat_id 9) → `dataset/coco-boat-subset/` (boat-only class 0, split 80/10/10).
- `train_military_yolo.py` (root) — **✓ XONG 29/10**: train + val multi-GPU
  (`data=dataset/heretic-8c/heretic-8c.yaml`, imgsz=640, epochs=30, batch=64, device=0,1),
  copy best → `weights/yolo26n-military-8c.pt`, in mAP tổng + per-class.
- `requirements-lock.txt` (root) — **✓ XONG 29/10**: pin ultralytics 8.4.162 + torch 2.14.0
  + torchvision 0.29.0 (cu130) — server == laptop.
- `weights/` — thư mục chứa weight sau train (chỉ commit file `.pt` cuối cùng; `.gitignore` draft).

**Modify**
- `heretic_phase4_hud.py` — `:184` `YOLO("yolo26n.pt")` → đọc từ flag `--model` (default `yolo26n.pt`).
- `tactical_slm.py` — `:31` `DANGEROUS_TARGETS` bỏ `person`, thêm `soldier` + `military_vehicle`;
  `:35-42` `SYSTEM_PROMPT` mapping tiếng Việt (kẻ địch / xe quân sự địch / dân thường).

**Delete** — không.

## Implementation Steps

1. **W3d1** — test truy cập Baidu pan **trên server** (tải 1 file). Nếu không được: dùng
   AMAD hoặc InvictusRex (GitHub release) — ghi nguồn thực tế vào register B5.
2. **W3d2** — `datasets/prepare_mvrsd.py`: extract ảnh + label, map class MVRSD → 8 class
   (mọi label xe quân sự → `military_vehicle`; bỏ label máy bay; ảnh chỉ chứa class
   ngoài scope → bỏ), split 80/20, sinh `datasets/mvrsd-8c.yaml`.
3. **W3d3** — **research nguồn ảnh `soldier` (B9)**: tìm dataset mở (GitHub: military person /
   soldier detection); phương án dự phòng: tự ghi footage thao trường + label (cần đồng ý).
   Chốt trước train W4d1; không có nguồn → **escalate giảng viên (giữ 7 class), không tự hạ**.
   Mapping MVRSD: mọi label xe quân sự (tank/IFV/pháo/…) → `military_vehicle`; bỏ label máy bay.
4. **W3d4** — prep VisDrone subset 5 class (person, car, motorcycle, truck, bus) — góc drone
   (đáp ứng "dataset thu từ UAV" — yêu cầu giảng viên 2026-10-16); verify license +
   **đọc dataset card MVRSD + VisDrone: ghi tham số thu (độ cao, tốc độ, FOV) vào `docs/`**
   (báo cáo đồ án).
5. **W3d5** — prep COCO subset 6 class (~2000 ảnh train + val) cho trộn chống regression.
   *(Nếu UAV về tay trước W4: quay footage 360P ở độ cao 30–50m, tốc độ 3–5 m/s,
   target 10–50m — gold standard, đồng thời là nguồn `soldier`.)*
6. **W4d1–2** — `train_military_yolo.py`: `yolo detect train model=yolo26n.pt
   data=datasets/mvrsd-8c.yaml imgsz=640 epochs=30 batch=64 device=0,1`
   (MVRSD + VisDrone + nguồn `soldier` + COCO subset trộn trong 1 yaml). Chạy overnight,
   `CUDA_VISIBLE_DEVICES=0,1` (multi-GPU — đẩy nhanh fine-tune, quyết định 2026-10-15).
   Trước khi train: sinh `requirements-lock.txt` (version `ultralytics`, `torch`, `torchvision`
   trên server) và install đúng version đó trên laptop.
7. **W4d3** — val: `yolo detect val model=weights/yolo26n-military-8c.pt
   data=datasets/mvrsd-8c.yaml split=val` → mAP50 (cần ≥0.75).
8. **W4d3** — regression COCO: val model cũ + model mới trên COCO subset 6 class →
   chênh mAP50 ≤5 điểm.
9. **W4d4** — copy weight sang laptop; `python heretic_phase4_hud.py --model weights/yolo26n-military-8c.pt`
   trên 1 clip có lính + xe quân sự → box `soldier` + box `military_vehicle` + SLM cảnh báo.
10. **W4d5** — update `tactical_slm.py` (DANGEROUS_TARGETS + prompt); pipe payload có
   `soldier` + `military_vehicle` vào `python tactical_slm.py` → câu cảnh báo "kẻ địch" /
   "xe quân sự địch"; payload `person` → không cảnh báo (dân thường).

## Success Criteria

- [ ] `yolo detect val ... split=val` (MVRSD + VisDrone + soldier): **mAP50 ≥ 0.75** — **AC7**
- [ ] COCO subset 6 class: mAP50 model mới ≥ mAP50 model cũ − 5 điểm — **AC7**
- [ ] VisDrone subset 5 class hợp lệ + **tham số thu UAV (độ cao/tốc độ/FOV) verify từ
      dataset card + ghi trong báo cáo** — **AC7** (đặc thù UAV, yêu cầu giảng viên)
- [ ] Clip có lính + xe quân sự: box `soldier` + box `military_vehicle` hiện + SLM in
      "CẢNH BÁO: ..." "kẻ địch" / "xe quân sự địch" — **AC7**
- [ ] `requirements-lock.txt` commit; laptop install đúng version → `--model
      weights/yolo26n-military-8c.pt` chạy trên RTX 3050 — **AC7**
- [ ] Weight chạy trên laptop: ≥20fps @720p GPU (đo 30s đầu vòng lặp) — non-functional
- [ ] `python tactical_slm.py --demo` mỗi câu <1.5s (warm) — **AC10** (không regression)
- [ ] `datasets/mvrsd-8c.yaml` + `train_military_yolo.py` commit, train reproducible

## Risk Assessment

| Rủi ro | Mitigation |
|--------|-----------|
| Baidu pan không truy cập được từ server (B5) | Fallback AMAD / InvictusRex (GitHub release); nếu dataset thay → map lại class, re-run W3d2–3 (còn trong W3) |
| Fine-tune làm degrade 6 class COCO cũ | Trộn MVRSD + COCO subset trong 1 train; nếu regression >5điểm → tăng tỉ lệ COCO / hạ lr, iterate tối đa 2 lần |
| mAP50 <0.75 sau 30 epochs | Tăng epochs (50) / bật mosaic-mixup augmentation; nếu dataset quá nhỏ không đạt → báo giảng viên điều chỉnh ngưỡng **trước** W11, không tự ý hạ |
| Không có nguồn ảnh `soldier` (B9) | Research W3d3; ưu tiên footage UAV thật tự quay (khi UAV về); fallback: tự ghi footage thao trường + label (cần đồng ý); nếu vẫn không có → **escalate giảng viên trước W4d1** (giữ 7 class), không tự ý giảm scope |
| VisDrone license / tham số thu không như kỳ vọng | Verify license + dataset card ở W3d4; fallback: MVRSD + COCO + footage tự quay — ghi trade-off "ít ảnh góc drone" trong báo cáo |
| Mất cân bằng class `soldier` (ít ảnh hơn MVRSD) | Trộn tỉ lệ: giới hạn số ảnh MVRSD / tăng augment cho `soldier`; val theo-class, không chỉ mAP tổng |
| Server bị tranh dụng (4×Ada dùng chung) | `CUDA_VISIBLE_DEVICES=0` + chạy overnight; backup: 1 GPU Ada vẫn dư cho batch 32 |
