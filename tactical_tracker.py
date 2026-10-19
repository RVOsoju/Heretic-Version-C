"""
Heretic Version C - Phase 1: TrackStore (song kem ByteTrack)

Giur history (t, cx_px, cy_px, dist_m, scale) per track_id trong cua so
5 khung -> tinh:
  - velocity (m/s)  = Δpx/Δt × scale khung cuoi (toan phan van toc)
  - approach (m/s)  = -d(dist_m)/dt (duong = target dang toi gan)

Track khong cap nhat > 2s (mat) bi prune. Chi chay CPU, khong an VRAM.
"""

import math
import time

DEFAULT_WINDOW = 5     # so khung giu lai per track
DEFAULT_MAX_AGE_S = 2.0  # track mat > 2s -> xoa


class TrackStore:
    def __init__(self, window=DEFAULT_WINDOW, max_age_s=DEFAULT_MAX_AGE_S):
        self.window = window
        self.max_age_s = max_age_s
        self.tracks = {}  # track_id -> [(ts, cx_px, cy_px, dist_m, scale), ...]

    def update(self, track_id, ts, cx_px, cy_px, dist_m, scale):
        """Mo mot khung moi cua track. scale = he so m/px cua khung (de tinh velocity)."""
        hist = self.tracks.setdefault(track_id, [])
        hist.append((ts, cx_px, cy_px, dist_m, scale))
        if len(hist) > self.window:
            del hist[: len(hist) - self.window]

    def _span(self, track_id):
        """Tra (first, last, dt) cua cua so, hoac None neu du thieu du lieu."""
        hist = self.tracks.get(track_id)
        if not hist or len(hist) < 2:
            return None
        first, last = hist[0], hist[-1]
        dt = last[0] - first[0]
        if dt <= 0:
            return None
        return first, last, dt

    def velocity(self, track_id):
        """Toan phan van toc (m/s) giua 2 khung dau/cuoi cua so."""
        span = self._span(track_id)
        if span is None:
            return 0.0
        (_, x0, y0, _d0, _s0), (_, x1, y1, _d1, s1), dt = span
        dp = math.hypot(x1 - x0, y1 - y0)
        return dp / dt * s1

    def approach(self, track_id):
        """Toc do tiep can (m/s): -d(dist_m)/dt — duong = dang toi gan."""
        span = self._span(track_id)
        if span is None:
            return 0.0
        (_, _x0, _y0, d0, _s0), (_, _x1, _y1, d1, _s1), dt = span
        return (d0 - d1) / dt

    def prune(self, now=None):
        """Xoa cac track khong cap nhat > max_age_s (track mat)."""
        now = time.time() if now is None else now
        stale = [tid for tid, h in self.tracks.items()
                 if now - h[-1][0] > self.max_age_s]
        for tid in stale:
            del self.tracks[tid]
