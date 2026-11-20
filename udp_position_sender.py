"""
Heretic Version C - Node telemetry: phat vi tri GPS 1Hz qua UDP

Mo phong 1 node dong doi/UAV (thay firmware ESP32 khi chua co phan cuong):
di theo toc do khong doi, phat JSON {"id","lat","lon","t"} den laptop.
Format goi = chinh xac tactical_telemetry_feed.py.

Chay tren node 2 (dien thoai/laptop 2), trong mang rieng voi laptop:
  .venv/bin/python udp_position_sender.py --target 192.168.137.1
  .venv/bin/python udp_position_sender.py --id uav --speed 3.0 --offset-m 40
  .venv/bin/python udp_position_sender.py --duration 60   # phat 60s roi dung
"""
import argparse
import json
import math
import socket
import time

from tactical_telemetry_feed import EARTH_M_PER_DEG_LAT, TELEMETRY_PORT

SOLDIER_DEFAULT = (21.0333, 105.7333)  # Tu Liem, Ha Noi


def offset(lat, lon, bearing_deg, dist_m):
    """Diem cach (lat, lon) dist_m theo bearing do la ban (0=Bac, 90=Dong)."""
    b = math.radians(bearing_deg)
    dlat = dist_m * math.cos(b) / EARTH_M_PER_DEG_LAT
    dlon = dist_m * math.sin(b) / (EARTH_M_PER_DEG_LAT * math.cos(math.radians(lat)))
    return lat + dlat, lon + dlon


class PositionSim:
    """Duong di toc do khong doi tu vi tri goi — ground truth cho bench."""

    def __init__(self, lat0, lon0, bearing_deg, speed_mps, t0=None):
        self.lat0, self.lon0 = lat0, lon0
        self.bearing_deg = bearing_deg
        self.speed = speed_mps
        self.t0 = t0 if t0 is not None else time.time()

    def position_at(self, t):
        """(lat, lon) tai thoi diem t — closed-form, de kiem toa do nhan duoc."""
        return offset(self.lat0, self.lon0, self.bearing_deg,
                      self.speed * max(0.0, t - self.t0))


def main():
    parser = argparse.ArgumentParser(
        description="Phat vi tri GPS mo phong 1Hz qua UDP (node dong doi/UAV)")
    parser.add_argument("--id", default="ally-1",
                        help="node id goi trong payload (mac dinh ally-1)")
    parser.add_argument("--target", default="127.0.0.1",
                        help="IP cua laptop (mac dinh 127.0.0.1 = test local)")
    parser.add_argument("--port", type=int, default=TELEMETRY_PORT,
                        help=f"port UDP (mac dinh {TELEMETRY_PORT})")
    parser.add_argument("--lat", type=float, default=SOLDIER_DEFAULT[0],
                        help="vita do lich (diem tham chieu)")
    parser.add_argument("--lon", type=float, default=SOLDIER_DEFAULT[1])
    parser.add_argument("--offset-m", type=float, default=20.0,
                        help="khoang cach bat dau so voi lich (mac dinh 20m)")
    parser.add_argument("--bearing", type=float, default=90.0,
                        help="huong di, do la ban (0=Bac, 90=Dong; mac dinh 90)")
    parser.add_argument("--speed", type=float, default=1.4,
                        help="toc do m/s (mac dinh 1.4 = bo hang)")
    parser.add_argument("--interval", type=float, default=1.0,
                        help="gian cach giay/goi (mac dinh 1Hz)")
    parser.add_argument("--duration", type=float, default=0.0,
                        help="so giay phat (0 = den khi Ctrl+C)")
    args = parser.parse_args()

    start = offset(args.lat, args.lon, args.bearing, args.offset_m)
    sim = PositionSim(start[0], start[1], args.bearing, args.speed)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    end_t = time.time() + args.duration if args.duration > 0 else None
    print(f"[NODE] {args.id}: phat 1/{args.interval:g}s -> {args.target}:{args.port} "
          f"(bat dau {args.offset_m:.0f}m, {args.speed} m/s, huong {args.bearing:.0f} do)")
    try:
        while True:
            now = time.time()
            if end_t is not None and now >= end_t:
                break
            lat, lon = sim.position_at(now)
            sock.sendto(json.dumps({"id": args.id, "lat": lat, "lon": lon,
                                    "t": now}).encode(), (args.target, args.port))
            print(f"[{now - sim.t0:6.1f}s] {args.id} {lat:.6f} {lon:.6f}")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()
    print("[NODE] Dung phat.")


if __name__ == "__main__":
    main()
