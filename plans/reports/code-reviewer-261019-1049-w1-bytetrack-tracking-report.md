# Code Review — W1 ByteTrack Tracking (final)

Reviewer: code-reviewer | 2026-10-19 | Scope: W1 diff (uncommitted)

## Scope
- Files: `heretic_phase4_hud.py` (M, 234 ln), `tactical_tracker.py` (NEW, 66), `tactical_slm.py` (M, 179), `test_360p_precision.py` (NEW, 133); deleted `heretic_phase1.py`, `heretic_phase2.py`; plan.md B6 row updated.
- Carried over from prior session: py_compile 4/4, telemetry chain 11/11, 360p P 0.74 / R 0.79, gater/TrackStore sims, deleted-file ref check.
- This session: live-sim run (exit 0, 16/16 `sim_hud_*_quiet.png` — all quiet because Ollama is CPU-only and times out on this box; environmental, not a code failure), plus re-verification of `box.id` API and gater semantics.

## Verdict per acceptance criterion

**(a) Gater keyed by track_id; 100m crossing → exactly 1 alert; sim fallback identical — PASS.**
- `tactical_slm.py:56-60` `_key()`: `track_id` if present else `(target, bearing)`.
- Empirical (this session, real `TacticalAlertGater`): fresh track crossing 100m → 1 alert on first sub-100m frame, then 10 m/1 m steps; re-entry (>100 m) pops key and re-arms (`tactical_slm.py:66-68`).
- Sim path (`heretic_phase4_hud.py:177-180`) builds threat dicts with no `track_id` → `_key` returns the pre-W1 tuple → identical 16/16 alerting sequence (verified by simulation).
- `evaluate_alert` records `last_warned` only for the closest alerting threat (`tactical_slm.py:107-108`) — pre-W1 semantics, unchanged. Multi-track sim (2 ids, same bearing): each track gets its `last_warned` entry within ~2 frames; structurally ≤1 SLM call/frame. No missed/extra gating beyond design.

**(b) No --sim / telemetry regression — PASS.**
- `--sim` branch untouched (`heretic_phase4_hud.py:172-191`); payload gains `track_id: null, approach_mps: null` fields — harmless to Ollama prompt and to gater.
- `test_telemetry_chain.py` imports (`enemies_payload`, `make_sim_frame`, `minimap_units_from_feed`) all exist with unchanged signatures; `TelemetryFeed`/`is_friendly_by_gps`/`read_soldier_gps` untouched (`tactical_telemetry_feed.py` not in diff).
- Live sim: exit 0, 16/16 PNGs written.

**(c) No breaking signature changes — PASS.** `build_tactical_data` gains optional kwargs only (`heretic_phase4_hud.py:61-62`); `enemies_payload`, `TacticalAlertGater` API unchanged.

**(d) Matches codebase patterns — PASS.** kebab-case module, Vietnamese docstrings, 66-line focused module, no plan/finding refs in code comments, `ts` captured once per frame (`heretic_phase4_hud.py:218`) so TrackStore dt is consistent.

**(e) No new syntax/lint errors — PASS.** `py_compile` 4/4 OK (re-run this session).

## Verified risk points
- `int(box.id[0])` (`heretic_phase4_hud.py:72`): empirically confirmed on ultralytics 8.4.162 — per-box `box.id` is a shape `(1,)` tensor, `int(box.id[0])` valid; `box.id is None` when not tracking (guarded). Correct.
- Gater `last_warned` never pruned: bounded by ByteTrack id count (monotonic, no reuse within a tracker instance → no false gating from id reuse); KB-scale even for long sessions. Acceptable.
- `test_360p_precision.py:94` affine: `v - (x0 if k % 2 == 0 else y0)` maps `[x1,y1,x2,y2]` → window coords correctly (x→x0, y→y0).

## Issues (no BLOCKER / no MAJOR)
1. **MINOR** — `last_warned` unbounded (`tactical_slm.py:53,108`). Bounded by created track count; acceptable. Optional: prune stale keys alongside `tracker.prune()`.
2. **MINOR** — `heretic_phase4_hud.py` 234 lines > 200 guideline (pre-existing; W1 net +7). Candidate: extract sim loop.
3. **MINOR** — `test_360p_precision.py` GT circularity: GT = yolo26n on the 720p canvas, so P/R is self-consistency, not absolute accuracy. Documented in docstring + plan B6 row; retest on real UAV frames is already planned.
4. **MINOR** — `docs/laptop-deployment-guide.md:75` references `sim_hud_*m_alert.png`; with CPU-only Ollama the sim writes `*_quiet.png`. Stale on this machine, correct on GPU box with Ollama.
5. **MINOR** — `assets/` (bus-360p.mp4, bus-720p-canvas.jpg) untracked. Regenerable by the script; commit for reproducibility. `yolo26n.pt` untracked (pre-existing state).

## Positive observations
- Clean optional-injection design (`tracker=None, ts=None`) keeps sim/demo/telemetry paths untouched.
- `tactical_slm.py` docstring updated from phase2 → phase4 pipe reference; no dangling refs to deleted phase1/phase2 files (grep-verified).
- TrackStore is small, pure-CPU, well-documented; 5-frame window + 2 s prune is a sensible default.

## Recommended actions
1. Commit `assets/` with the test script.
2. Optional: stale-key sweep in gater; extract sim loop if file grows further.
3. Update deployment guide line 75 to `sim_hud_*m_{alert,quiet}.png`.

**Status:** DONE
