# W1 Complete: ByteTrack Tracking + Tactical Data in One Day

**Date**: 2026-10-19
**Severity**: Low (routine milestone)
**Component**: heretic_phase4_hud.py, tactical_tracker.py, tactical_slm.py, test_360p_precision.py
**Status**: Resolved (W1d1–W1d5 done, uncommitted)

## What Happened

W1 (tracking week) finished in a single day: ByteTrack wired into the HUD, new `tactical_tracker.py` (66 lines) with TrackStore (velocity m/s, approach m/s, 2s prune, 5-frame window), `build_tactical_data()` + `enemies_payload()` carrying `track_id` + `approach_mps` (backward compatible — sim path untouched), and `TacticalAlertGater._key()` preferring `track_id` with (target, bearing) fallback.

## Key Technical Results

- **Baseline first**: test_telemetry_chain.py 11/11 PASS + `--sim` 16/16 frames verified BEFORE any code change. Post-W1: 16/16 again, alert cadence identical on the fallback key. No regressions.
- **ByteTrack overhead: 1.5ms/frame** (model() 15ms vs model.track() 16ms) — under the 5ms budget. Verified on synthetic 360P video (assets/bus-360p.mp4, 30 frames; no webcam on dev server): 3 person track IDs (1/2/12), 0 re-IDs.
- **360P precision (blind spot B6, step 1)**: precision 0.74 / recall 0.79 at conf ≥0.25, person ~170px in 640×360 window. Caveat: ground truth is the same model at 720p affinely transformed (circularity), and 170px is large vs real UAV targets (16–40px). Logged as first data point in plan.md B6; real-UAV retest pending.
- **Deviation from plan**: `update()` gained a `scale` param so velocity is in m/s, not px/s. Deliberate, documented.
- Review: 5 MINOR, 0 BLOCKER/MAJOR. Notable: `last_warned` dict unbounded (acceptable — ByteTrack IDs bounded), heretic_phase4_hud.py at 234 lines (> 200 guideline, pre-existing trend).

## Environment Notes

Dev-server Ollama (localhost:11434) is CPU-only → 10s read timeouts in sim runs (all frames "quiet"). Environmental, not a code issue; real SLM verification happens on the target laptop (GPU Ollama :11435).

## Lessons

Verify-before-change paid off: the 16/16 baseline made "no regression" a measurable claim, not a hope. Also: synthetic assets (bus.jpg) are fine for plumbing validation but must never be quoted as field performance — the 0.74/0.79 is explicitly a circular-GT first data point.

## Next

W2: object-height anchor, flash HUD (AC4), test_tracking.py for AC1/AC2, AC3 gater 100m test. Not committed — user commits/pushes per standing rule.
