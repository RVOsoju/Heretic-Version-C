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

from tactical_height_anchor import (FALLBACK_SCALE, MIN_ANCHOR_BOX_H_PX, SIM_FOV_DEG,
                                    SIM_UAV_ALT_M, height_anchor_scale, sim_frame_scale)
from tactical_hud_renderer import WARN_RANGE_M, render_hud
from tactical_slm import TacticalAlertGater, call_ollama, evaluate_alert
from tactical_telemetry_feed import TelemetryFeed, is_friendly_by_gps, read_soldier_gps
from tactical_tracker import TrackStore

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
PIXEL_TO_METER = FALLBACK_SCALE  # fallback m/px; moi box dung object-height anchor
SOLDIER_GPS = {"lat": 21.0333, "lon": 105.7333, "location": "Tu Liem, Ha Noi"}


def is_friendly(t):
    """HOOK nhan biet dong doi (che do ko telemetry): luon False.
    Khi --telemetry, main() dung is_friendly_by_gps() thay the (dong doi =
    nguoi co module GPS NEO-6M, tin hieu con moi trong ban kinh) - dong doi
    se duoc ve xanh tren HUD/minimap va KHONG bat canh bao SLM."""
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


def build_tactical_data(results, center_x, center_y, scale, model_names, friendly_fn=None,
                        tracker=None, ts=None):
    """List box YOLO -> list {target, track_id, distance_m, bearing, approach_mps, box, side}.
    friendly_fn: ham nhan biet dong doi (None -> het thuc la dich).
    tracker+ts: TrackStore (Phase 1) — neu co, mo tung track + tinh approach_mps.
    scale: fallback m/px; moi box tu do dung object-height anchor (class/box_h)."""
    tactical = []
    for r in results:
        for box in r.boxes:
            class_name = model_names[int(box.cls[0])]
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            box_scale = height_anchor_scale(class_name, y2 - y1, scale)
            distance, direction = calculate_tactical_telemetry(box, center_x, center_y, box_scale)
            track_id = int(box.id[0]) if box.id is not None else None
            t = {
                "target": class_name,
                "track_id": track_id,
                "distance_m": distance,
                "bearing": direction,
                "box": (x1, y1, x2, y2),
            }
            if tracker is not None and track_id is not None and ts is not None:
                tracker.update(track_id, ts, (x1 + x2) / 2, (y1 + y2) / 2, distance, box_scale)
                t["approach_mps"] = round(tracker.approach(track_id), 2)
            t["side"] = "friendly" if friendly_fn and friendly_fn(t) else "enemy"
            tactical.append(t)
    return tactical


def enemies_payload(tactical):
    """Payload SLM tu cac unit DIC duy nhat (dong doi khong duoc bat canh bao).
    Mang theo track_id + approach_mps de gater ngat ngan theo track, khong lap."""
    return {"soldier_gps": SOLDIER_GPS,
            "detected_threats": [
                {"target": t["target"], "distance_m": t["distance_m"],
                 "bearing": t["bearing"], "track_id": t.get("track_id"),
                 "approach_mps": t.get("approach_mps")}
                for t in tactical if t.get("side", "enemy") == "enemy"]}


def minimap_units_from_feed(feed, soldier_latlon):
    """Tin hieu GPS -> (uav_frac, gps_units) cho minimap.
    uav_frac: toa do (fx, fy) trong [0,1], tam = lich, canh = 100m.
    gps_units: [(dx_m, dy_m, 'friendly')] cac don doi con tin hieu.
    Khong feed / khong tin hieu: vi tri UAV mo phong, khong dot dong doi."""
    if feed is None or not soldier_latlon:
        return (0.15, 0.18), []
    rel = feed.relative_positions(soldier_latlon)
    uav = rel.pop("uav", None)
    if uav:
        fx = 0.5 + max(-1.0, min(1.0, uav[0] / WARN_RANGE_M)) * 0.5
        fy = 0.5 - max(-1.0, min(1.0, uav[1] / WARN_RANGE_M)) * 0.5
        uav_frac = (fx, fy)
    else:
        uav_frac = (0.15, 0.18)
    gps_units = [(dx, dy, "friendly") for dx, dy in rel.values()]
    return uav_frac, gps_units


def make_sim_frame(distance_m, direction, alt_m=SIM_UAV_ALT_M, fov_deg=SIM_FOV_DEG):
    """Khung hinh hop thanh 1280x720 + mot 'dich' (person) di den gan theo khoang cach.
    Vat ly sim: UAV bay h=alt_m, FOV ngang fov_deg → scale = 2h.tan(FOV/2)/W;
    chieu cao box nguoi = 1.7m/scale (object-height anchor doc duoc lai tu do).
    Target xa hon bien khung → gap ve bien khung (kich thuoc box van dung)."""
    frame = np.full((FRAME_HEIGHT, FRAME_WIDTH, 3), (15, 18, 15), dtype=np.uint8)
    for i in range(1, 10):  # luoi nen
        x = FRAME_WIDTH * i // 10
        y = FRAME_HEIGHT * i // 10
        cv2.line(frame, (x, 0), (x, FRAME_HEIGHT), (30, 35, 30), 1)
        cv2.line(frame, (0, y), (FRAME_WIDTH, y), (30, 35, 30), 1)
    scale = sim_frame_scale(FRAME_WIDTH, alt_m, fov_deg)
    person_h = max(MIN_ANCHOR_BOX_H_PX, int(1.7 / scale))
    person_w = max(8, int(0.5 / scale))
    cx, cy = FRAME_WIDTH // 2, FRAME_HEIGHT // 2
    px = {"Đông": (1, 0), "Bắc": (0, -1), "Tây": (-1, 0), "Nam": (0, 1)}[direction]
    tx = cx + px[0] * int(distance_m / scale)
    ty = cy + px[1] * int(distance_m / scale)
    tx = max(person_w, min(FRAME_WIDTH - person_w, tx))
    ty = max(person_h, min(FRAME_HEIGHT - person_h, ty))
    r_head = max(4, person_w // 3)
    cv2.circle(frame, (tx, ty - person_h // 2), r_head, (60, 60, 60), -1)
    cv2.rectangle(frame, (tx - person_w // 2, ty - person_h // 2 + r_head),
                  (tx + person_w // 2, ty + person_h // 2), (60, 60, 60), -1)
    return frame, (tx - person_w // 2, ty - person_h // 2, tx + person_w // 2, ty + person_h // 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sim", action="store_true",
                        help="Chế độ hợp thành: không cần webcam, lưu screenshot")
    parser.add_argument("--telemetry", action="store_true",
                        help="Bật feed GPS UDP (port 8888): nhan bien dong doi + vi tri UAV/ally")
    parser.add_argument("--soldier-gps", metavar="LAT,LON",
                        help="Toa do lich thu cong, vi du: 21.0333,105.7333")
    parser.add_argument("--gps-port", metavar="PORT",
                        help="Doc NEO-6M cua lich qua USB TTL, vi du: /dev/ttyUSB0 (Windows: COM5)")
    parser.add_argument("--cpu", action="store_true",
                        help="Chay YOLO tren CPU - de nguyen VRAM cho SLM (laptop 4GB VRAM)")
    parser.add_argument("--slm", action="store_true",
                        help="Bat SLM Ollama cho cau canh bao (mac dinh: template, khong can Ollama)")
    args = parser.parse_args()

    # Toa do lich: --gps-port (phan cuong) > --soldier-gps (thua tay) > muc dinh
    soldier_latlon = None
    if args.gps_port:
        soldier_latlon = read_soldier_gps(args.gps_port)
        print(f"[GPS] Doc NEO-6M tu {args.gps_port}: {soldier_latlon}")
    if args.soldier_gps:
        lat, lon = (float(v) for v in args.soldier_gps.split(","))
        soldier_latlon = (lat, lon)
    if not soldier_latlon:
        soldier_latlon = (SOLDIER_GPS["lat"], SOLDIER_GPS["lon"])
    SOLDIER_GPS["lat"], SOLDIER_GPS["lon"] = soldier_latlon

    feed = TelemetryFeed().start() if args.telemetry else None
    if feed:
        print("[TELEMETRY] Dang nghe tin hieu GPS UDP port 8888")

    # DONG DOI = nguoi co GPS con moi; khong feed -> het thuc la dich
    friendly_fn = (lambda t: is_friendly_by_gps(t, feed, soldier_latlon)) if feed else None

    gater = TacticalAlertGater()
    tracker = TrackStore()

    if args.sim:
        sim_box = None
        flash_left = 0
        print("[SIM] HUD hop thanh: binh lanh tiep can huong Tay 95m -> 1m")
        for distance in [95, 90, 85, 75, 65, 55, 45, 35, 25, 15, 9, 8, 7, 5, 3, 1]:
            frame, sim_box = make_sim_frame(distance, "Tây")
            t = {"target": "person", "distance_m": distance,
                 "bearing": "Tây", "box": sim_box}
            t["side"] = "friendly" if friendly_fn and friendly_fn(t) else "enemy"
            tactical = [t]
            alert = evaluate_alert(enemies_payload(tactical), gater, use_slm=args.slm)
            flash_left = 3 if alert else max(0, flash_left - 1)  # flash 3 khung
            uav_frac, gps_units = minimap_units_from_feed(feed, soldier_latlon)
            out = render_hud(frame, tactical, alert, time.time(), uav_frac, gps_units,
                             flash=flash_left > 0)
            tag = "alert" if alert else "quiet"
            path = f"sim_hud_{distance}m_{tag}.png"
            cv2.imwrite(path, out)
            print(f"[{distance}m] {tag}: {alert or '-'} -> {path}")
            time.sleep(0.1)
        if feed:
            feed.stop()
        return

    print("[INFO] Dang nap mo hinh YOLO...")
    from ultralytics import YOLO
    model = YOLO("yolo26n.pt")

    # Warmup SLM chi khi --slm (mac dinh: template 0ms, khong can Ollama)
    if args.slm:
        try:
            call_ollama("Tra ve dung 1 tu: An toan", timeout=120)
            print("[INFO] SLM da nong, san sang canh bao.")
        except Exception as exc:
            print(f"[CANH CAO] SLM chua san sang (Ollama chua chay?) — de duoc cai template: {exc}")

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cx, cy = FRAME_WIDTH // 2, FRAME_HEIGHT // 2
    print("🔥 [HERETIC C - PHASE 4] HUD san sang. Bam 'q' de thoat.")

    yolo_device = "cpu" if args.cpu else None
    flash_left = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        results = model.track(frame, persist=True, tracker="bytetrack.yaml",
                              stream=False, verbose=False, device=yolo_device)
        tactical = build_tactical_data(results, cx, cy, PIXEL_TO_METER, model.names,
                                       friendly_fn, tracker=tracker, ts=time.time())
        tracker.prune()
        alert = evaluate_alert(enemies_payload(tactical), gater, use_slm=args.slm)
        flash_left = 3 if alert else max(0, flash_left - 1)  # flash 3 khung (~100ms @30fps, khong am)
        uav_frac, gps_units = minimap_units_from_feed(feed, soldier_latlon)
        cv2.imshow("Heretic Tactical HUD - Phase 4",
                   render_hud(frame, tactical, alert, time.time(), uav_frac, gps_units,
                              flash=flash_left > 0))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    if feed:
        feed.stop()


if __name__ == "__main__":
    main()
