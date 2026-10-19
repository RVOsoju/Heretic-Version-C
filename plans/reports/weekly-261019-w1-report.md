# Weekly Report — W1 (19/10–25/10)

**Plan:** `plans/261015-1637-phase5-3-month-roadmap/` · **Hoàn thành W1 trong 1 ngày (19/10)**
**Kế tiếp:** W2 = 26/10–01/11 — đầu tuần đọc lại report này + `plan.md` rồi tiếp tục.

## 1. Đã làm

| # | Việc | Kết quả | Bằng chứng |
|---|------|---------|------------|
| W1d1 | ByteTrack tracking | `model.track(persist=True, bytetrack.yaml)` — 0 re-ID/30 khung, overhead **1.5ms < 5ms** | `heretic_phase4_hud.py` |
| W1d2 | TrackStore | `tactical_tracker.py` (66 dòng): velocity/approach/prune (cửa sổ 5 khung, 2s) | mới |
| W1d3 | Payload | `track_id` + `approach_mps` vào tactical dict + payload (backward-compat) | — |
| W1d4 | Gater theo track_id | `_key()` ưu tiên `track_id`, fallback `(target, bearing)` — sim/demo không đổi | `tactical_slm.py` |
| W1d5 | Test 360P (B6 step 1) | 30 frame 640×360: **P 0.74 / R 0.79** (person ~170px — retest máy thật khi UAV về) | `test_360p_precision.py` |
| + | **Kênh câu chữ hybrid** | template = **chính** (0ms, 0 VRAM, không Ollama); SLM optional `--slm`; Ollama fail → fallback template (kênh câu không bao giờ chết) | `tactical_slm.py`, `heretic_phase4_hud.py` |
| + | Cleanup | Xóa `heretic_phase1.py`, `heretic_phase2.py` (prototype cũ) | git |

## 2. Quyết định kỹ thuật (chốt W1)

| Quyết định | Lý do |
|------------|-------|
| **Template chính, SLM optional** | LLM không làm logic gì (gater/khoảng cách/closest/flash đều backend); 3b Q4 ăn ~2GB/4GB VRAM; template luôn sống (0ms). SLM giữ làm câu "có hồn" cho màn C2, advisory. |
| **Giữ YOLO 26n** (không lên 26l) | 26l @360P ≈ 2–3GB + SLM 2GB = **OOM 4GB**; `--cpu` 26l ≈ 2–5fps (vi phạm AC8 ≥15fps). Card train (5000 Ada) không liên quan VRAM inference. Fallback: W4 nếu mAP50 <0.75 → thử 26s + bench VRAM laptop. |
| **Quantization SLM: giữ Q4_K_M** (default tag `qwen2.5:3b`, ~2GB) | Sweet spot VRAM/chất lượng; Q2_K ~1.4GB nhưng giảm chất lượng tiếng Việt. Độ chính xác khóa bằng `temperature=0, num_predict=20, stop=["\n"]`. |

## 3. Kiểm thử & review

- `test_telemetry_chain.py`: **14/14 PASS** (+3 check hybrid: câu template đúng, gater lần 1 báo, lần 2 im)
- `--sim`: **2.6s** (trước ~2,5 phút do 13× timeout Ollama) — 15 khung `*_alert.png`
- `--demo` chạy không cần Ollama
- tester 6/6 · code-reviewer 2 lần (W1 + hybrid): **5/5 PASS, 0 blocker/maJOR**; MINOR 1 fixed (`95.0m`→`95m`)

## 4. Files chờ commit (1 commit, user tự push)

- Modify: `tactical_slm.py`, `heretic_phase4_hud.py`, `test_telemetry_chain.py`
- Create: `tactical_tracker.py` (**bắt buộc cùng 3 file trên — thiếu là repo gãy**), `test_360p_precision.py`
- Assets: `assets/bus-720p-canvas.jpg`, `assets/bus-360p.mp4`
- Docs/plans: PDR, briefing, `plan.md`, `phase-01-*.md`, PM report + review report, journal
- `yolo26n.pt` (5.3MB) — auto-download, nên .gitignore

## 5. Unresolved

1. **B4**: kiểm kho ESP32+NEO-6M (deadline W1 — việc user; nếu không có → đường sim, code đã hỗ trợ).
2. Commit W1 (list §4) — user.
3. Live webcam chưa verify (dev server không có webcam) — verify trên laptop TUF F15 (W2/W6).
4. 360P P/R hiện là trên video tổng hợp — retest khi UAV về (B6 step 2).

## 6. W2 kế hoạch (26/10–01/11)

| Ngày | Việc | AC |
|------|------|----|
| W2d1 | **Object-height anchor**: scale = kích thước thật class / chiều cao box (px), tự hiệu chuẩn mỗi khung, fallback 0.05 khi box <8px; cập nhật physics `make_sim_frame` | S1 (±15–25%) |
| W2d2 | **Flash HUD** cảnh báo im lặng (gater trigger → flash) | AC4 (<100ms, không phát âm) |
| W2d3–4 | `test_tracking.py` mới: 1 người di chuyển liên tục ≥100 khung | AC1 (re-ID <5%) + AC2 (vận tốc tiếp cận sai <10%) |
| W2d5 | `test_telemetry_chain.py` cập nhật: gater 100m — cắt ngưỡng 1 lần = 1 cảnh báo; payload 3 target → chọn gần nhất | AC3 |

→ Xong W2 = **M1 done (AC1–AC3)**.
