# W2 Complete: Object-Height Anchor + Flash HUD, M1 Done (AC1–AC4)

**Date**: 2026-10-26
**Severity**: Low (routine milestone)
**Component**: tactical_height_anchor.py (new), heretic_phase4_hud.py, test_tracking.py (new), test_telemetry_chain.py
**Status**: Resolved (W2d1–W2d5 done in one day, M1 complete — AC1–AC4)

## What Happened

W2 (distance + AC4 week) closed M1 in a single day. The constant `PIXEL_TO_METER=0.05` — wrong by ×1.5–3 at 30–50m UAV altitude — was replaced by a per-box object-height anchor: `tactical_height_anchor.py` computes scale m/px = real class height / box_h (px), falling back to 0.05 when the class is missing or box_h < 8px. `sim_frame_scale()` = 2h·tan(FOV/2)/W is the sim ground truth (h=30m, FOV 60°). `build_tactical_data` now computes per-box scale, and `make_sim_frame` was rewritten with real sim physics: person box = 1.7m/scale ≈ 62px tall (was a 130px blob), far targets clamp to the frame edge (visible ground half-width at 30m/60° is only 17.3m).

## Key Technical Results

- **Anchor accuracy**: synthetic 15m/10m frames → 1.2–1.3% distance error (threshold was <25%; the old constant would have erred ×1.92). Because the sim emits frames from a known scale and the anchor recovers it, this is a true round-trip test — the W1 360P circularity caveat doesn't apply here.
- **Flash HUD (AC4)**: `render_hud(flash=)` full-screen red overlay; gater trigger → 3 frames @30fps ≈ 100ms; no audio API (OPSEC). Verified in sim PNGs — the 90m quiet frame is red, the 2nd decay frame after the 95m alert.
- **test_tracking.py (new, AC1/AC2)**: 150 frames @30fps, 62px person sprite (cropped from ultralytics assets/bus.jpg) moving 1100→680px, real YOLO26n + ByteTrack @imgsz=1280. Detection 150/150, re-ID 0.0% (AC1 <5%), approach velocity 2.32 vs GT 2.29 m/s = 1.2% error (AC2 <10%).
- **AC3** into test_telemetry_chain.py (+6 checks → 20 total): 105m→95m same track_id = exactly 1 alert; repeat 95m = silent; 3 targets (95/42/60m) → closest 42m chosen.
- **Review**: 5/5 PASS, 0 BLOCKER/MAJOR, 3 MINOR all fixed immediately.

## Notable Debugging

- **imgsz=640 → 0 detections**: the 62px person was too small after default downscale. The test would have "passed" on the wrong axis until raw detections were inspected. Fixed by pinning imgsz=1280 (native 720p, matches PDR runtime).
- **The "full track" lie**: `full_track_approach` was reading `store.tracks`, which TrackStore trims to a 5-frame window — it measured a window, not the full track, and passed because constant velocity makes both values identical. Fixed: accumulate (ts, dist) locally. A test that measures the wrong thing and passes is worse than a failing test.
- Removed tautological check `3/30.0 <= 0.1`; stripped plan references (W2/AC4) from implementation comments per project rule (test files keep AC refs for traceability).
- 1 pre-existing note left as-is (W1-accepted): gater records `last_warned` only for the closest alerting target.

## Lessons

The anchor was the satisfying one: a one-line formula (real height / box height) beat a miscalibrated constant, and the physics-based sim turned the distance test from circular into round-trip. The 640 failure mode is the sharper lesson — synthetic tests can pass on the wrong axis; always look at raw detections, not just the aggregate metric.

## Next

M1 (AC1–AC4) complete; phase-01 marked completed with evidence, plan.md W2 ✓ + Session 9 validation log, weekly report `plans/reports/weekly-261026-w2-report.md`, PDR + supervisor-briefing headers updated (anchor is implemented, no longer "từ W2"). W3 per plan. Not committed — user commits/pushes per standing rule.
