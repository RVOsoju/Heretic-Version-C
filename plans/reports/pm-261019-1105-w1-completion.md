# PM Report — W1 Completion (2026-10-19)

**Plan:** `plans/261015-1637-phase5-3-month-roadmap/` · **Phase 1** (Tracking ByteTrack + gater track_id)

## Progress

| Hạng mục | Trạng thái | Bằng chứng |
|----------|-----------|------------|
| Baseline đầu tuần | ✓ | `test_telemetry_chain.py` 11/11 · `--sim` 16/16 khung |
| W1d1 ByteTrack | ✓ | `model.track(persist=True, bytetrack.yaml)` — 0 re-ID/30 khung · overhead **1.5ms <5ms** |
| W1d2 TrackStore | ✓ | `tactical_tracker.py` (66 dòng): velocity/approach/prune, 5 khung, 2s |
| W1d3 payload | ✓ | `track_id` + `approach_mps` vào tactical dict + payload SLM (backward-compat) |
| W1d4 gater re-key | ✓ | `_key()` ưu tiên `track_id`, fallback `(target, bearing)` — sim không đổi |
| W1d5 360P (B6) | ✓ | `test_360p_precision.py`: 30 frame 640×360, **P 0.74 / R 0.79** |
| Cleanup | ✓ | Xóa `heretic_phase1.py`, `heretic_phase2.py` (prototype cũ) |
| Review | ✓ | tester 6/6 PASS · code-reviewer a–e PASS, 0 BLOCKER/MAJOR |

**Phase 1:** W1 ✓ (19/10) — còn W2 (object-height anchor, flash HUD AC4, `test_tracking.py` AC1/AC2, AC3 gater 100m) → M1.
**Toàn plan:** 1/12 tuần (W2 = 26/10–01/11 tiếp theo).

## Files

- Modify: `heretic_phase4_hud.py` (track + TrackStore + payload), `tactical_slm.py` (`_key`)
- Create: `tactical_tracker.py`, `test_360p_precision.py`, `assets/bus-720p-canvas.jpg`, `assets/bus-360p.mp4`
- Delete: `heretic_phase1.py`, `heretic_phase2.py`
- `yolo26n.pt` (5.3MB, auto-download) — chưa track trong git

## Docs impact

**None** — PDR/deployment guide không bị ảnh hưởng (thay đổi nội bộ pipeline; `model.track` trong suốt với cách chạy).

## Unresolved

1. **B4** (node ESP32+NEO-6M trong kho?) — việc vật lý của user, deadline W1; nếu không có → đường sim (code đã hỗ trợ).
2. `assets/` + `yolo26n.pt` chưa commit — nên commit assets (reproducibility test 360P); weight 5.3MB auto-download được (có thể .gitignore).
3. Ollama dev server (11434) CPU-only timeout — sim trên máy này luôn "quiet"; cảnh báo thật verify trên laptop (11435 GPU).
4. Live webcam path chưa verify trên dev server (không có webcam) — verify trên laptop TUF F15 (W2/W6).
