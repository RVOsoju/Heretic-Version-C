"""
Heretic Version C - Object-height anchor

Scale m/px tu chieu cao box: scale = kich thuc that class / box_h (px),
tu hieu chuan moi khung — thay constant 0.05 (chi dung ~15-22m, sai x1.5-3
o do cao bay 30-50m). Fallback 0.05 khi class khong co trong bang hoac
box_h < 8px (qua xa, box khong du tin).
"""
import math

# Kich thuc that (m) theo class — chieu cao / kich thuc chieu thuong
CLASS_HEIGHT_M = {
    "person": 1.7, "soldier": 1.7,
    "car": 1.5, "motorcycle": 1.6,
    "truck": 3.5, "bus": 3.5,
    "boat": 1.5, "military_vehicle": 3.0,
}
MIN_ANCHOR_BOX_H_PX = 8
FALLBACK_SCALE = 0.05  # scale cu (hieu chuan ~15-22m)

# Tham so sim: UAV bay h=30m, FOV ngang 60° — ground truth cho test anchor
SIM_UAV_ALT_M = 30.0
SIM_FOV_DEG = 60.0


def height_anchor_scale(class_name, box_h_px, fallback=FALLBACK_SCALE):
    """Scale m/px = kich thuc that / box_h (px); fallback neu box qua nho/khong co class."""
    h_m = CLASS_HEIGHT_M.get(class_name)
    if h_m is None or box_h_px < MIN_ANCHOR_BOX_H_PX:
        return fallback
    return h_m / box_h_px


def sim_frame_scale(frame_width, alt_m=SIM_UAV_ALT_M, fov_deg=SIM_FOV_DEG):
    """Scale m/px cua khung sim: do rong mat dat thay = 2h.tan(FOV/2), chan nen frame_width px."""
    return 2.0 * alt_m * math.tan(math.radians(fov_deg) / 2.0) / frame_width
