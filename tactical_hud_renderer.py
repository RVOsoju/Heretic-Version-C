"""
Heretic Version C - Phase 4: Tactical HUD renderer

Hac thuac ham ve OpenCV (frame numpy in -> frame numpy ra), khong phu thuoc
mau hinh/manifest: muon di sang LCD 7-inch chi can doi dia chi xuat hien
thanh phan render_hud() nay.

Thanh phan HUD:
  - Khung bounding box kiểu quân sự (góc chữ L): đỏ = địch, xanh = lính mình
  - Minimap 2D góc phải trên: 3 chấm UAV (xanh lá), Lính (xanh dương), Địch (đỏ)
  - Thanh cảnh báo SLM chớp nháy ở đáy màn hình
"""

import cv2

# Mau sac BGR
RED = (0, 0, 255)        # dich
BLUE = (255, 180, 0)     # lich minh / dong doi
GREEN = (0, 200, 0)      # UAV
YELLOW = (0, 255, 255)   # chu canh bao
DARK = (25, 20, 20)

# Phuong vi (Phase 2) -> vector don vi toa do anh (x tang phai, y tang xuoi duoi)
BEARING_VEC = {"Đông": (1, 0), "Bắc": (0, -1), "Tây": (-1, 0), "Nam": (0, 1)}

MINIMAP_SIZE = 200
WARN_RANGE_M = 100.0     # khoang cach toc do cua minimap: 100m = ra canh map


def _text(frame, text, org, color, scale=0.55, thick=1, shadow=True):
    """putText co bong dem de doc duoc tren nen tuoi (cam)."""
    if shadow:
        cv2.putText(frame, text, (org[0] + 1, org[1] + 1),
                    cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thick + 1, cv2.LINE_AA)
    cv2.putText(frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick, cv2.LINE_AA)


def draw_military_bbox(frame, x1, y1, x2, y2, color, label):
    """Khung kiểu quân sư: 8 goc chu L thay vi khung hinh chuu nhat kín."""
    L = max(12, int(0.22 * min(x2 - x1, y2 - y1)))
    t = 2
    pts = [(x1, y1, 1, 1), (x2, y1, -1, 1), (x1, y2, 1, -1), (x2, y2, -1, -1)]
    for cx, cy, sx, sy in pts:
        cv2.line(frame, (cx, cy), (cx + sx * L, cy), color, t, cv2.LINE_AA)
        cv2.line(frame, (cx, cy), (cx, cy + sy * L), color, t, cv2.LINE_AA)
    _text(frame, label, (x1, max(0, y1 - 8)), color, 0.55, 1)


def draw_soldier_marker(frame, cx, cy):
    """Lich minh (tam khung hinh): dau ngoac xanh duong + nhan."""
    cv2.drawMarker(frame, (cx, cy), BLUE, cv2.MARKER_CROSS, 22, 3, cv2.LINE_AA)
    _text(frame, "SOLDIER", (cx + 14, cy + 5), BLUE, 0.5, 1)


def draw_minimap(frame, uav_frac, units, gps_units=()):
    """Minimap goc phai tren. uav_frac: toa do (fx, fy) trong [0,1].
    units: list (distance_m, bearing, side) tu box YOLO - 'enemy' dot do, 'friendly' dot xanh.
    gps_units: list (dx_m, dy_m, side) - don doi co vi tri GPS thuc, ve theo toa do relative."""
    s = MINIMAP_SIZE
    ox, oy = frame.shape[1] - s - 12, 12

    cv2.rectangle(frame, (ox, oy), (ox + s, oy + s), DARK, -1)
    cv2.rectangle(frame, (ox, oy), (ox + s, oy + s), (0, 120, 0), 1)
    for i in range(1, 4):  # luoi 4x4
        cv2.line(frame, (ox + i * s // 4, oy), (ox + i * s // 4, oy + s), (0, 60, 0), 1)
        cv2.line(frame, (ox, oy + i * s // 4), (ox + s, oy + i * s // 4), (0, 60, 0), 1)
    _text(frame, "MINIMAP", (ox + 6, oy + 16), (0, 200, 0), 0.45, 1)

    cx, cy = ox + s // 2, oy + s // 2
    px_per_m = (s / 2 - 12) / WARN_RANGE_M

    # Dich (do) / dong doi (xanh): theo huong + khoang cach, giam trong khung map
    for dist, bearing, side in units:
        v = BEARING_VEC.get(bearing, (0, 0))
        d = min(float(dist), WARN_RANGE_M)
        ex = int(cx + v[0] * d * px_per_m)
        ey = int(cy + v[1] * d * px_per_m)
        ex = max(ox + 4, min(ox + s - 4, ex))
        ey = max(oy + 4, min(oy + s - 4, ey))
        color = BLUE if side == "friendly" else RED
        cv2.circle(frame, (ex, ey), 5, color, -1, cv2.LINE_AA)
        cv2.circle(frame, (ex, ey), 8, color, 1, cv2.LINE_AA)

    # Don doi (xanh): vi tri GPS thuc quy ve quanh lich (dy > 0 = Bac = len len)
    for dx, dy, side in gps_units:
        ex = int(cx + dx * px_per_m)
        ey = int(cy - dy * px_per_m)
        ex = max(ox + 4, min(ox + s - 4, ex))
        ey = max(oy + 4, min(oy + s - 4, ey))
        color = BLUE if side == "friendly" else RED
        cv2.circle(frame, (ex, ey), 5, color, -1, cv2.LINE_AA)
        cv2.circle(frame, (ex, ey), 8, color, 1, cv2.LINE_AA)

    # UAV (xanh la): vi tri tu feed hoac mo phong
    ux = ox + int(uav_frac[0] * s)
    uy = oy + int(uav_frac[1] * s)
    cv2.circle(frame, (ux, uy), 5, GREEN, -1, cv2.LINE_AA)
    _text(frame, "UAV", (ux + 8, uy + 4), GREEN, 0.4, 1)

    # LICH MINH (xanh duong): tam
    cv2.circle(frame, (cx, cy), 6, BLUE, -1, cv2.LINE_AA)
    cv2.circle(frame, (cx, cy), 10, BLUE, 1, cv2.LINE_AA)


def draw_alert_bar(frame, text, blink_on):
    """Thanh đáy: do chan no khi blink_on (2Hz), do xam khi off. Khong co
    text -> thanh xanh lá "AN TOAN" on din."""
    h, w = frame.shape[:2]
    bar_h = 54
    y0 = h - bar_h
    has_alert = text is not None

    if has_alert and blink_on:
        bg, fg = (120, 0, 0), YELLOW
        body = text[:90]
    elif has_alert:
        bg, fg, body = (35, 15, 15), (0, 120, 120), ""
    else:
        bg, fg = (10, 40, 10), (0, 220, 0)
        body = "AN TOAN - KHONG CANH BAO"

    cv2.rectangle(frame, (0, y0), (w, h), bg, -1)
    cv2.line(frame, (0, y0), (w, y0), (0, 255, 255), 1, cv2.LINE_AA)
    if body:
        (tw, th), _ = cv2.getTextSize(body, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        _text(frame, body, ((w - tw) // 2, y0 + bar_h // 2 + th // 2), fg, 0.8, 2)


def render_hud(frame, tactical_data, alert_text, now, uav_frac=(0.15, 0.18), gps_units=()):
    """Gop toan bo HUD len khung hinh. tactical_data: list {target, distance_m,
    bearing}. alert_text: cau SLM hoac None. now: thoi diem (s) cho nhap chop.
    uav_frac: vi tri UAV tren minimap (tu feed GPS). gps_units: don doi theo GPS thuc."""
    h, w = frame.shape[:2]

    draw_soldier_marker(frame, w // 2, h // 2)

    for t in tactical_data:
        x1, y1, x2, y2 = t["box"]
        side = t.get("side", "enemy")
        name = "DONG DOI" if side == "friendly" else "DICH"
        color = BLUE if side == "friendly" else RED
        label = f"{name} {t['distance_m']}m {t['bearing'].upper()}"
        draw_military_bbox(frame, x1, y1, x2, y2, color, label)

    draw_minimap(frame, uav_frac=uav_frac,
                 units=[(t["distance_m"], t["bearing"], t.get("side", "enemy"))
                        for t in tactical_data],
                 gps_units=gps_units)

    blink_on = int(now * 2) % 2 == 0  # nhap 2Hz: 0.25s bat - 0.25s tat
    draw_alert_bar(frame, alert_text, blink_on)
    return frame
