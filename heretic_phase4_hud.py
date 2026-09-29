"""
Heretic Version C - Phase 4: Tactical HUD + Minimap

Giao dien HUD: video trung tam + khung dich kieu quan su + minimap 2D
(UAV/Lich/Dich) + thanh canh bao SLM nhap chop o day man hinh.

Chay:
  python heretic_phase4_hud.py            # webcam thuc + YOLO
  python heretic_phase4_hud.py --sim      # ko webcam: khung hinh hop thanh
                                           # + tinh binh tiep can 95m->1m
                                           # (de test HUD headless, luu anh)

LCD 7-inch: render_hud() la ham thanh -> chi can doi phan hien thi
(cv2.imshow) sang phan xuat anh ra man hinh LCD.
"""

import argparse
import time

import cv2
import numpy as np

from tactical_hud_renderer import render_hud
from tactical_slm import TacticalAlertGater, evaluate_alert

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
PIXEL_TO_METER = 0.05  # he so quy doi gia lung (Phase 2): 1 px = 0.05 m
SOLDIER_GPS = {"lat": 21.0333, "lon": 105.7333, "location": "Tu Liem, Ha Noi"}


def is_friendly(t):
    """HOOK nhan biet dong doi: hien luon False (chua co phan canh tag).
    Sau nay cam nguon du lieu vao day (RF tag, ID tren mu, whitelist GPS...)
    - dong doi se duoc ve xanh tren HUD/minimap va KHONG bat canh bao SLM."""
    return False


def calculate_tactical_telemetry(box, center_x, center_y, scale):
    """Khoang cach (m) + huong tu tam (lich) den tam box - nhap tu Phase 2."""
    import math
    x1, y1, x2, y2 = box.xyxy[0].tolist()
    dx = (x1 + x2) / 2 - center_x
    dy = center_y - (y1 + y2) / 2
    distance = round(math.sqrt(dx**2 + dy**2) * scale, 1)
    angle_deg = math.degrees(math.atan2(dy, dx))
    if -45 <= angle_deg <= 45:
        direction = "Đông"
    elif 45 < angle_deg < 135:
        direction = "Bắc"
    elif 135 <= abs(angle_deg) <= 180:
        direction = "Tây"
    else:
        direction = "Nam"
    return distance, direction


def build_tactical_data(results, center_x, center_y, scale, model_names):
    """List box YOLO -> list {target, distance_m, bearing, box, side} cho renderer."""
    tactical = []
    for r in results:
        for box in r.boxes:
            class_name = model_names[int(box.cls[0])]
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            distance, direction = calculate_tactical_telemetry(box, center_x, center_y, scale)
            t = {
                "target": class_name,
                "distance_m": distance,
                "bearing": direction,
                "box": (x1, y1, x2, y2),
            }
            t["side"] = "friendly" if is_friendly(t) else "enemy"
            tactical.append(t)
    return tactical


def enemies_payload(tactical):
    """Payload SLM tu cac unit DIC duy nhat (dong doi khong duoc bat canh bao)."""
    return {"soldier_gps": SOLDIER_GPS,
            "detected_threats": [
                {"target": t["target"], "distance_m": t["distance_m"],
                 "bearing": t["bearing"]}
                for t in tactical if t.get("side", "enemy") == "enemy"]}


def make_sim_frame(distance_m, direction):
    """Khung hinh hop thanh 1280x720 + mot 'dich' di den gan theo khoang cach."""
    frame = np.full((FRAME_HEIGHT, FRAME_WIDTH, 3), (15, 18, 15), dtype=np.uint8)
    for i in range(1, 10):  # luoi nen
        x = FRAME_WIDTH * i // 10
        y = FRAME_HEIGHT * i // 10
        cv2.line(frame, (x, 0), (x, FRAME_HEIGHT), (30, 35, 30), 1)
        cv2.line(frame, (0, y), (FRAME_WIDTH, y), (30, 35, 30), 1)
    # 'Dich': hinh nguoi don gian, vi tri theo huong + khoang cach (px = m/0.05)
    cx, cy = FRAME_WIDTH // 2, FRAME_HEIGHT // 2
    px = {"Đông": (1, 0), "Bắc": (0, -1), "Tây": (-1, 0), "Nam": (0, 1)}[direction]
    dist_px = int(min(distance_m / PIXEL_TO_METER, 620))
    tx, ty = cx + px[0] * dist_px, cy + px[1] * dist_px
    cv2.circle(frame, (tx, ty - 40), 18, (60, 60, 60), -1)
    cv2.rectangle(frame, (tx - 22, ty - 20), (tx + 22, ty + 50), (60, 60, 60), -1)
    return frame, (tx - 40, ty - 70, tx + 40, ty + 60)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sim", action="store_true",
                        help="Chế độ hợp thành: không cần webcam, lưu screenshot")
    args = parser.parse_args()

    gater = TacticalAlertGater()

    if args.sim:
        sim_box = None
        print("[SIM] HUD hop thanh: binh lanh tiep can huong Tay 95m -> 1m")
        for distance in [95, 90, 85, 75, 65, 55, 45, 35, 25, 15, 9, 8, 7, 5, 3, 1]:
            frame, sim_box = make_sim_frame(distance, "Tây")
            tactical = [{"target": "person", "distance_m": distance,
                         "bearing": "Tây", "box": sim_box, "side": "enemy"}]
            alert = evaluate_alert(enemies_payload(tactical), gater)
            out = render_hud(frame, tactical, alert, time.time())
            tag = "alert" if alert else "quiet"
            path = f"sim_hud_{distance}m_{tag}.png"
            cv2.imwrite(path, out)
            print(f"[{distance}m] {tag}: {alert or '-'} -> {path}")
            time.sleep(0.1)
        return

    print("[INFO] Dang nap mo hinh YOLO...")
    from ultralytics import YOLO
    model = YOLO("yolo26n.pt")

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cx, cy = FRAME_WIDTH // 2, FRAME_HEIGHT // 2
    print("🔥 [HERETIC C - PHASE 4] HUD san sang. Bam 'q' de thoat.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        results = model(frame, stream=False, verbose=False)
        tactical = build_tactical_data(results, cx, cy, PIXEL_TO_METER, model.names)
        alert = evaluate_alert(enemies_payload(tactical), gater)
        cv2.imshow("Heretic Tactical HUD - Phase 4",
                   render_hud(frame, tactical, alert, time.time()))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
