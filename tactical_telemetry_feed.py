"""
Heretic Version C - Telemetry: nguon vi tri GPS (UAV + dong doi)

Nhan broadcast vi tri qua UDP (JSON ~30B) tu cac node ESP32:
  {"id": "uav", "lat": 21.0333, "lon": 105.7333, "t": 1727600000.12}
  {"id": "ally-1", "lat": ..., "lon": ..., "t": ...}

Vi sao UDP thay vi MQTT: 2-3 node @1Hz -> khong can broker, don gian
hon, khong co diem that dong nhat. Khi he thong lan ra 10+ node, thay
module nay bang MQTT (giao dien class giu nguyen).

Kiem toa do equirectangular (doi hoi ~8m) du chinh xac, khong can
haversine day du.
"""

import json
import math
import socket
import threading
import time

TELEMETRY_PORT = 8888
STALE_AFTER_S = 5.0        # tin hieu coi la "mat" neu > 5s khong goi
FRIENDLY_MATCH_M = 8.0     # ban kinh khớp box YOLO <-> vi tri dong doi
EARTH_M_PER_DEG_LAT = 111320.0

# Phuong vi (Phase 2) -> goc la ban do (0 = Dong, 90 = Bac, ccw)
BEARING_COMPASS = {"Đông": 0.0, "Bắc": 90.0, "Tây": 180.0, "Nam": 270.0}


class TelemetryFeed:
    """UDP listener nen: giu vi tri moi nhat moi node id."""

    def __init__(self, port=TELEMETRY_PORT, host="0.0.0.0"):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((host, port))
        self._sock.settimeout(0.2)
        self._latest = {}  # id -> (lat, lon, recv_time)
        self._running = True

    def _listen(self):
        while self._running:
            try:
                data, _ = self._sock.recvfrom(512)
                pkt = json.loads(data)
                self._latest[pkt["id"]] = (
                    float(pkt["lat"]), float(pkt["lon"]), time.time())
            except socket.timeout:
                continue
            except Exception:
                continue  # goi hu (khong JSON) bo luon

    def start(self):
        threading.Thread(target=self._listen, daemon=True).start()
        return self

    def stop(self):
        self._running = False
        self._sock.close()

    def fresh(self, node_id, max_age_s=STALE_AFTER_S):
        """(lat, lon) neu tin hieu con moi, khong thi None."""
        pos = self._latest.get(node_id)
        if pos and time.time() - pos[2] <= max_age_s:
            return pos[0], pos[1]
        return None

    def relative_positions(self, soldier_latlon, max_age_s=STALE_AFTER_S):
        """dict id -> (dx_m, dy_m) tuan do quy uoc anh (x phai, y xuoi duoi)
        quy ve quanh lich, tu cac tin hieu con moi."""
        if not soldier_latlon:
            return {}
        slat, slon = soldier_latlon
        out = {}
        for nid, (lat, lon, t) in self._latest.items():
            if time.time() - t > max_age_s:
                continue
            dy = (lat - slat) * EARTH_M_PER_DEG_LAT
            dx = (lon - slon) * EARTH_M_PER_DEG_LAT * math.cos(math.radians(slat))
            out[nid] = (dx, dy)
        return out


def point_offset(lat, lon, bearing, dist_m):
    """Chuyen (huong, khoang cach) truoc camera diem (lat, lon) - de khop
    vi tri YOLO voi vi tri GPS dong doi."""
    rad = math.radians(90.0 - BEARING_COMPASS[bearing])
    dlat = dist_m * math.cos(rad) / EARTH_M_PER_DEG_LAT
    dlon = dist_m * math.sin(rad) / (EARTH_M_PER_DEG_LAT * math.cos(math.radians(lat)))
    return lat + dlat, lon + dlon


def flat_dist_m(lat1, lon1, lat2, lon2):
    """Khoang cach (m) equirectangular - du dung cho ban kinh ~8m."""
    dy = (lat2 - lat1) * EARTH_M_PER_DEG_LAT
    dx = (lon2 - lon1) * EARTH_M_PER_DEG_LAT * math.cos(math.radians(lat1))
    return math.hypot(dx, dy)


def is_friendly_by_gps(t, feed, soldier_latlon, radius_m=FRIENDLY_MATCH_M):
    """HOOK: muc tieu la dong doi neu co vi tri dong doi moi trong ban kinh
    quanh vi tri ty duoc cuua no (lich + huong + khoang cach)."""
    if feed is None or not soldier_latlon:
        return False
    slat, slon = soldier_latlon
    tlat, tlon = point_offset(slat, slon, t["bearing"], t["distance_m"])
    rel = feed.relative_positions(soldier_latlon)
    for nid in rel:
        if nid == "uav":
            continue
        alat = slat + rel[nid][1] / EARTH_M_PER_DEG_LAT
        alon = slon + rel[nid][0] / (EARTH_M_PER_DEG_LAT * math.cos(math.radians(slat)))
        if flat_dist_m(tlat, tlon, alat, alon) <= radius_m:
            return True
    return False


def _nmea_coord(val, hemi):
    """NMEA '2102.123' + 'N' -> 21.03538 (so thap phan)."""
    degrees = float(val[:2])
    minutes = float(val[2:])
    value = degrees + minutes / 60.0
    if hemi in ("S", "W"):
        value = -value
    return value


def read_soldier_gps(port, tries=15, baud=9600):
    """Doc lat/lon tu NEO-6M cua chinh lich (NMEA $GPRMC qua USB TTL).
    Tra ve (lat, lon) hoac None neu module chua co fix."""
    import serial  # import muon: chi can khi co thuc te GPS
    ser = serial.Serial(port, baud, timeout=1.0)
    try:
        for _ in range(tries):
            line = ser.readline().decode(errors="ignore").strip()
            if line.startswith("$GPRMC") and ",A," in line:
                p = line.split(",")
                return _nmea_coord(p[3], p[4]), _nmea_coord(p[5], p[6])
    finally:
        ser.close()
    return None
