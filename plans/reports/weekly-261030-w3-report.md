# Weekly Report — tổng hợp tuần 26/10–01/11 (W3 data + W4 prep, xong sớm)

**Plan:** `plans/261015-1637-phase5-3-month-roadmap/`
**Mốc tuần:** W2 done 26/10 (M1) → W3 data **XONG SỚM 27–28/10** → W4 prep **XONG SỚM 29/10** → SLM 8-class 30/10
**Kế tiếp:** W4 = 09/11–15/11 — fine-tune yolo26n → 8 class trên server 4×Ada (chạy qua đêm).

## 1. Đã làm

| # | Việc | Kết quả | Bằng chứng |
|---|------|---------|------------|
| (W2, 26/10) | tracking + anchor + flash | M1 done (AC1–AC4) — chi tiết trong `weekly-261026-w2-report.md` | 20/20 + 7/7 checks |
| W3 (27/10) | 4 nguồn dataset tải + verify | MVRSD 13,582 (mirror InvictusRex → **B5 đóng**) · VisDrone 9,209 (HuggingFace) · Mendeley 7,985 (CC BY 4.0) · COCO boat 3,025 | `dataset/` (gitignored) |
| W3 (27/10) | **Mendeley verify = B9 đóng sớm** | 7,985 ảnh / 16,341 box (soldier 3,436); map Soldier→soldier, Tank→military_vehicle, People→person, Drone→loại (952 ảnh negative); fix 782 label thiếu newline | render spot-check 4/4 |
| W3 (28/10) | **COCO boat subset** | `prepare_coco_boat_subset.py` — cat_id 9, 3,025 ảnh / 10,576 box, split 80/10/10 | bug catch: draft dùng cat_id 51 = **bowl** → visual check bắt, sửa → 9 |
| W3 (28/10) | **heretic-8c merge** | `prepare_heretic_8c_dataset.py` → **33,221 ảnh** (train 26,691/val 3,343/test 3,187), 8 class, **452,552 box** | 0 malformed, class ID ∈[0,7], coord ∈[0,1] |
| W3 (29/10) | **Bảng tham số thu 4 nguồn** | `docs/dataset-capture-parameters.md` (AC7 — báo cáo đồ án): platform/độ cao/tốc độ/FOV/res + box theo class + license | 3/4 nguồn UAV, COCO boat = ground (ghi trung thực) |
| W4 prep (29/10) | train script + version lock | `train_military_yolo.py` (multi-GPU, per-class mAP `results.box.maps`) + `requirements-lock.txt` (ultralytics 8.4.162 / torch 2.14.0 / torchvision 0.29.0 cu130) | server == laptop |
| W4 prep (29/10) | dataset transfer (**hướng a**) | tarball 4 nguồn ~7GB → server, re-run `prepare_heretic_8c_dataset.py` trên server | không transfer merge (symlink bẻ + deref = cùng size, mất nguồn gốc) |
| W4d5 (30/10) | **SLM 8-class integration** | `tactical_slm.py`: `DANGEROUS_TARGETS` −person, `TARGET_LABELS` −person, `SYSTEM_PROMPT` +soldier/military_vehicle (bỏ qua person = dân thường); `heretic_phase4_hud.py`: `--model` flag (default `yolo26n.pt`) | person→im lặng, soldier→"Kẻ địch", military_vehicle→"Xe quân sự địch" |

## 2. Quyết định kỹ thuật (chốt tuần)

| Quyết định | Lý do |
|------------|-------|
| **4 nguồn merge = heretic-8c (33,221)** | 3/4 nguồn góc UAV (VisDrone/MVRSD/Mendeley) + COCO boat (ground, class phụ cảnh báo). Đáp ứng "dataset đặc thù UAV" (AC7, yêu cầu giảng viên 16/10). |
| **COCO boat = cat_id 9 (KHÔNG phải 51)** | 51 = bowl — bug catch qua visual check (render ra nồi bếp). Lesson: luôn verify category ID trong JSON + visual-check render trước khi merge. |
| **Không class-weighting trước (car 187k : soldier 3.4k ≈ 54:1)** | Train as-is → đọc per-class mAP → iterate (oversample soldier / tăng epochs) CHỈ NẾU soldier yếu ở W4. Không đoán trước, tránh over-engineer. |
| **Dataset transfer = hướng a (tarball 4 nguồn)** | `dataset/` gitignored → server clone KHÔNG có dataset. Chuyển 4 nguồn ~7GB, re-run prepare trên server. Bỏ COCO zip 19G (boat subset đã build sẵn 506M). |
| **SLM 8-class: `person` = dân thường, KHÔNG cảnh báo** | `person` ≠ `soldier`. Chỉ `soldier` (kẻ địch) + `military_vehicle` + 5 xe thường mới vào `DANGEROUS_TARGETS`. Person bị lọc trước gater → im lặng. |
| **`--model` flag (default `yolo26n.pt`)** | Chạy weight 8-class sau train mà không hardcode; backward compat (không flag = behavior cũ). |

## 3. Kiểm thử & review

- `test_telemetry_chain.py`: **20/20 PASS** (đã update 4 target vai-trò-địch `person`→`soldier`)
- `test_tracking.py`: **7/7 PASS** (không regression)
- SLM verify (30/10): `person`→im lặng · `soldier`→"Kẻ địch" · `military_vehicle`→"Xe quân sự địch" · `person(gần 10m)+soldier(45m)`→chỉ báo soldier · `--demo` gater nhịp 10m/1m đúng
- **code-review commit `b27a3043` (30/10): PASS** — 0 critical/important; `DANGEROUS_TARGETS` == `TARGET_LABELS` keys (7), `person` vắng cả 2; 0 secret leak
- compile sạch 3 file

## 4. Files (đã commit — user tự push)

- **Create:** `prepare_coco_boat_subset.py`, `prepare_heretic_8c_dataset.py`, `train_military_yolo.py`, `requirements-lock.txt`, `docs/dataset-capture-parameters.md`
- **Modify:** `tactical_slm.py`, `heretic_phase4_hud.py`, `test_telemetry_chain.py`
- `dataset/` — gitignored, **không commit**
- Commits tuần: `cd2b6f53` (COCO boat) · `2d2673f7` (train + lock) · `bd95a652` (capture params) · `b27a3043` (SLM 8-class)

## 5. Unresolved

1. **Fine-tune W4 chưa chạy** — cần server 4×Ada, chạy qua đêm (W4d1). Gate: mAP50 ≥0.75, COCO giảm ≤5đ.
2. **⚠ person↔soldier lẫn (risk chính — user nhấn mạnh):** code đúng (person→im lặng, soldier→báo), nhưng YOLO có thể nhãn nhầm lính đang tiếp cận → `person` → **không cảnh báo**. Mitigation: thêm ảnh `soldier` (Roboflow ~4.8k backup, **key đã có trong memory local**) trước/khi fine-tune W4 nếu soldier mAP yếu.
3. **Log sheet footage tự quay** — điền khi đi quay (i1 Pro / Mini 2 SE, độ cao 30–50m, 3–5 m/s, FOV đo).
4. **Mini 2 SE** — user mua, cần về trước W9 (field test).
5. **Live webcam chưa verify** (server không có webcam) — verify trên laptop TUF F15 (W6).

## 6. W4 kế hoạch (09/11–15/11) — M2: fine-tune 8 class

| Ngày | Việc | Verify |
|------|------|--------|
| W4d1 | Transfer tarball → server, extract, re-run `prepare_heretic_8c_dataset.py` | `heretic-8c.yaml` hợp lệ trên server |
| W4d1–2 | `train_military_yolo.py` (device=0,1, imgsz=640, epochs=30, batch=64) — **qua đêm** | `best.pt` + per-class mAP |
| W4d3 | val mAP50 (gate ≥0.75) + regression coco128 (giảm ≤5đ) | mAP50 ≥0.75 |
| W4d4 | copy weight laptop, `--model weights/yolo26n-military-8c.pt` chạy clip có lính + xe QS | box `soldier` + `military_vehicle` + SLM báo |
| W4d5 | SLM 8-class + `--model` flag | ✓ **done 30/10** |

→ **Nếu `soldier` mAP yếu:** pull Roboflow ~4.8k (key sẵn) → re-merge → re-train (giải quyết unresolved #2).
