"""
Test xich thac noi telemetry (ko can phan cuong that):
  UDP goi mo phong -> TelemetryFeed -> relative_positions
  -> is_friendly_by_gps -> minimap_units_from_feed -> render_hud

Chay: .venv/bin/python test_telemetry_chain.py
"""
import json
import math
import socket
import sys
import time

import cv2

from heretic_phase4_hud import enemies_payload, make_sim_frame, minimap_units_from_feed
from tactical_hud_renderer import render_hud
from tactical_telemetry_feed import (EARTH_M_PER_DEG_LAT, TelemetryFeed,
                                     is_friendly_by_gps)

TEST_PORT = 8899  # tranh xung dot port 8888 san xuat
SOLDIER = (21.0333, 105.7333)


def send_pos(sock, nid, lat, lon):
    sock.sendto(json.dumps({"id": nid, "lat": lat, "lon": lon,
                            "t": time.time()}).encode(), ("127.0.0.1", TEST_PORT))


def main():
    failures = []

    def check(name, cond, detail=""):
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")
        if not cond:
            failures.append(name)

    feed = TelemetryFeed(port=TEST_PORT, host="127.0.0.1").start()
    time.sleep(0.3)

    slat, slon = SOLDIER
    coslat = math.cos(math.radians(slat))
    # UAV: +30m Dong, +20m Bac; ally-1: -5m (Dong) - chinh xac 5m huong Tay
    uav = (slat + 20 / EARTH_M_PER_DEG_LAT,
           slon + 30 / (EARTH_M_PER_DEG_LAT * coslat))
    ally = (slat, slon - 5 / (EARTH_M_PER_DEG_LAT * coslat))
    tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_pos(tx, "uav", *uav)
    send_pos(tx, "ally-1", *ally)
    time.sleep(0.6)  # cho thread listen nhan het 2 goi

    rel = feed.relative_positions(SOLDIER)
    check("uau hien thu trong feed", "uav" in rel)
    if "uav" in rel:
        dx, dy = rel["uav"]
        check("UAV dx ~ +30m", abs(dx - 30) < 1.0, f"(dx={dx:.1f})")
        check("UAV dy ~ +20m", abs(dy - 20) < 1.0, f"(dy={dy:.1f})")
    check("ally-1 hien thu trong feed", "ally-1" in rel)
    if "ally-1" in rel:
        dx, _ = rel["ally-1"]
        check("ally dx ~ -5m", abs(dx + 5) < 1.0, f"(dx={dx:.1f})")

    # Dong doi: muc tieu nam chinh xac vi tri ally-1 (5m huong Tay)
    t_friendly = {"bearing": "Tây", "distance_m": 5.0}
    check("muc tieu o vi tri ally -> dong doi",
          is_friendly_by_gps(t_friendly, feed, SOLDIER))
    # Dich: 50m huong Dong, khong ally nao gan
    t_enemy = {"bearing": "Đông", "distance_m": 50.0}
    check("muc tieu 50m Dong -> dich", not is_friendly_by_gps(t_enemy, feed, SOLDIER))

    uav_frac, gps_units = minimap_units_from_feed(feed, SOLDIER)
    check("uav_frac khac vi tri mo phong", uav_frac != (0.15, 0.18), f"{uav_frac}")
    check("1 dot dong doi tren minimap", len(gps_units) == 1, f"{gps_units}")

    # Khung HUD: box sim o vi tri ally -> ve xanh (friendly), SLM im lang
    frame, box = make_sim_frame(5, "Tây")
    t = {"target": "person", "distance_m": 5.0, "bearing": "Tây", "box": box,
         "side": "friendly" if is_friendly_by_gps(t_friendly, feed, SOLDIER)
         else "enemy"}
    check("HUD phan loai friendly", t["side"] == "friendly")
    check("friendly khong vao payload SLM",
          enemies_payload([t])["detected_threats"] == [])
    path = "test_telemetry_chain_out.png"
    cv2.imwrite(path, render_hud(frame, [t], None, time.time(), uav_frac, gps_units))
    print(f"  [INFO] Anh kieu thuc -> {path}")

    tx.close()
    feed.stop()

    if failures:
        print(f"\n{len(failures)} check THAT BAI: {failures}")
        sys.exit(1)
    print("\nTOAN BO CHECK PASS")


if __name__ == "__main__":
    main()
