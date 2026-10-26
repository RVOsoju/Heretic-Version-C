# Code Review — W2: object-height anchor + gater AC3 + flash AC4

Reviewer: code-reviewer | 2026-10-26 | Scope: W2 diff (uncommitted, main)

## Scope
- Files: `tactical_height_anchor.py` (NEW, 37 ln), `heretic_phase4_hud.py` (M, 257 ln), `tactical_hud_renderer.py` (M, 159), `test_tracking.py` (NEW, 187), `test_telemetry_chain.py` (M, +36); 17 sim PNGs regenerated.
- Re-ran full suite this session: `test_telemetry_chain.py` 20/20 PASS; `test_tracking.py` 7/7 PASS (real YOLO26n + ByteTrack, 150 frames); `heretic_phase4_hud.py --sim` 16/16 frames, gater cadence 95→(90 quiet)→85…→1m correct; `py_compile` 5/5.
- Empirical probes: `height_anchor_scale` at h=0/-1/7/62; `make_sim_frame` box invariance at 1–500m × 4 bearings; flash overlay pixel analysis on sim PNGs; audio-API grep.

## Verdict per mandatory check

**(a) Acceptance criteria met by the CODE, not just test output — PASS (2 MINOR caveats).**
- W2d1 — `test_tracking.py:134-141` builds sim frames via `make_sim_frame(15/10, "Tây")` (defaults alt=30m, FOV=60°), reads the box, applies `height_anchor_scale("person", box_h)`, measures |box_center − frame_center|·s vs 15/10 m. Non-circular: GT from sim geometry (`sim_frame_scale` = 2h·tan(FOV/2)/W), measurement from anchor. Measured 15.2m/10.1m → 1.3% < 25%. Fallbacks asserted at :142-145 (box<8px, unknown class). PASS.
- AC1 — 150/150 frames detected; re-ID count logic sound (`test_tracking.py:163-169`: first-frame ids excluded, divisor `len(detected)-1` guarded by `max(1,·)`). 0.0% < 5%. PASS.
- AC2 — GT = 420px/149·30fps·0.027063 = 2.29 m/s (`:76-79`); measured 2.33 → 1.9% < 10%. PASS, **caveat 1** below.
- AC3 — `test_telemetry_chain.py:103-126`: 105m silent → 95m same track_id 7 → exactly 1 alert → repeat silent; 3 targets 95/42/60 → closest 42m chosen. Gater key/step logic verified at `tactical_slm.py:86-104`. PASS.
- AC4 — overlay check `:129-135` (frame diff with `flash=True/False`); empirical: sim PNGs red_ratio 0.84–0.86 with flash vs 0.29 without; `sim_hud_90m_quiet.png` is red = 2nd decay frame of the 95m alert, exactly the ≤3-frame design. No audio API anywhere in repo (grep: playsound/simpleaudio/winsound/pyaudio/sounddevice/.wav/.mp3 = 0 hits) → "no audio" is structural. PASS, **caveat 2** below.

**(b) No regression to existing business logic — PASS.**
- Live path `build_tactical_data` (`heretic_phase4_hud.py:70-88`): box_h=0 after int-truncation → `0 < 8` → fallback 0.05, no ZeroDivision (empirical h=0, h=-1, h=7 all → 0.05); class not in `CLASS_HEIGHT_M` → `.get` None → fallback (empirical "airplane"); `box.id is None` guarded (W1, unchanged :76). `model_names[int(box.cls[0])]` unchanged.
- `make_sim_frame` 2-arg calls (`test_telemetry_chain.py:78,129,132`) work — new params have defaults; test run green.
- `render_hud` existing 6-arg caller (`test_telemetry_chain.py:86`) works — `flash=False` default appended last.
- `--sim` 16/16 frames, gater cadence unchanged (95→90 quiet→85…1m).
- Intended behavior change (not regression): live distances now per-box anchored; e.g. person 62px → 0.0274 m/px vs old 0.05. Gater thresholds in meters shift accordingly — that is the W2d1 point.

**(c) No breaking changes to public contracts — PASS.**
- `build_tactical_data` signature unchanged (`scale` param semantics documented as fallback, :68).
- `enemies_payload` shape unchanged: `{soldier_gps, detected_threats:[{target, distance_m, bearing, track_id, approach_mps}]}` (:92-100); `t.get("approach_mps")` → None in sim, `template_alert` guards falsy (`tactical_slm.py:59-60`).
- `TrackStore` interface untouched; now fed `box_scale` per box (≈ frame scale for same-class targets — consistent).
- Gater key semantics unchanged (track_id, fallback (target, bearing)).
- `render_hud` / `make_sim_frame`: optional trailing params only.

**(d) Follows existing codebase patterns — PASS (1 MINOR note).**
- kebab-case module, no-diacritic Vietnamese docstrings in new module (consistent with `tactical_tracker.py`/`tactical_slm.py`), `check()` test pattern, no new dependencies (`tactical_height_anchor.py` imports only `math`), `numpy` import in renderer now used (flash overlay). File sizes: only `heretic_phase4_hud.py` 257 ln > 200 (pre-existing, accepted per task brief; W1 was 234).
- MINOR: plan-schedule refs in code — `tactical_height_anchor.py:2,21` ("W2"), `heretic_phase4_hud.py:198,241` ("AC4: flash 3 khung @30fps"), `test_tracking.py` header/check names ("W2d1", "AC1/AC2"). Project rule: code comments must not reference plan artifacts (they go stale). Codebase already carries "Phase N" refs (accepted in W1 review) and AC-named test checks are the house test convention → housekeeping, not blocking.

**(e) No new lint/syntax errors — PASS.** `py_compile` 5/5 this session. All imports used (verified: `MIN_ANCHOR_BOX_H_PX`, `SIM_FOV_DEG`, `SIM_UAV_ALT_M` in `make_sim_frame` defaults/body; `np` in renderer).

## Issues (no BLOCKER / no MAJOR)

1. **MINOR** — `test_tracking.py:112-119` `full_track_approach` docstring claims "TOÀN BỘ track — loại nhiễu jitter của cửa sổ 5 khung" but reads `store.tracks[tid]`, which `TrackStore.update` trims to a 5-frame window (`tactical_tracker.py:29-30`). It measures the last ~0.13 s, not the full track. For this constant-velocity test the two are identical (so AC2's 1.9% is genuinely valid), but the function misnames itself and will silently measure the wrong quantity if the test is extended to variable velocity (e.g. W3+). Fix: accumulate `(ts, dist)` per track in a local list inside `run_tracking` and compute (d0−d1)/dt from that.
2. **MINOR** — `test_telemetry_chain.py:136` `3 / 30.0 <= 0.1` is tautological (asserts an arithmetic constant, not behavior). The real 3-frame decay is observable in the sim PNG sequence and the live loop code (`heretic_phase4_hud.py:241`). Optional: drive a synthetic gater+flash loop and count flashed frames.
3. **MINOR** — "W2"/"AC4" plan refs in code comments (see (d)); rename to the invariant (e.g. "flash 3 khung sau trigger, ~100ms @30fps").
4. **MINOR (pre-existing, not a W2 change)** — `evaluate_alert` records `last_warned` only for the closest alerting threat (`tactical_slm.py:140-141`): with 3 simultaneous first-sighting targets, non-closest ones re-alert on the next frame until each gets recorded (self-stabilizes within N frames). Accepted in W1 report; noting for completeness.
5. **Observation** — sim loop runs at 10 steps/s (`time.sleep(0.1)`), so `flash_left=3` spans 3 PNGs ≈ 300 ms sim-time; the "@30fps" comment is only true for the live loop. Cosmetic — sim PNGs are a screenshot sequence, not a timeline.

## Positive observations
- `tactical_height_anchor.py` (37 ln) is a clean single source of truth; `PIXEL_TO_METER = FALLBACK_SCALE` removes the duplicated 0.05 literal.
- `make_sim_frame` now physically consistent (person box = 1.7m/scale ≈ 62px) → W2d1 is a true round-trip with real ground truth, no GT circularity (contrast: W1 360p GT-circularity note).
- Edge safety verified empirically: anchor guard covers box_h = 0/negative; `make_sim_frame` clamping keeps boxes in-frame with x1<x2, y1<y2 at 1–500 m × all 4 bearings (probed).
- `person_sprite()` looks up the person class by name (`[k for k,v in model.names.items() if v=="person"][0]`) — robust to COCO index order; loud `sys.exit` if the asset changes.
- Backward compat proven by execution, not inspection: all old call sites green.

## Recommended actions
1. Fix `full_track_approach` to use a locally accumulated full-track history (or rename to `window_approach` + docstring) before any variable-velocity test is added.
2. Optional: replace the tautological AC4 ms check with a frame-count check; strip "W2/AC4" plan refs from code comments.
3. No action needed on pre-existing gater multi-target recording (W1-accepted).

**Status:** DONE

## Unresolved questions
- Keep or clean the "W2/AC4" comment refs? (house-style question, non-blocking)
- Should AC2's "full track" be made real now (issue 1), or defer until a variable-velocity scenario is planned?
