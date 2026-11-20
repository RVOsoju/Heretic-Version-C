"""
AC5 bench: mang rieng + link loss (ko can phan cuong that)

Duong di thuc: udp_position_sender.PositionSim (1Hz) -> UDP -> TelemetryFeed
  A) feed nhan position ~1Hz, toa do sai <1m so ground truth sim
  B) cat link (dung sender) → feed.fresh() = None sau <=5s, khong crash,
     va feed van nhan duoc goi moi sau khi khoi phuc

Chay: .venv/bin/python test_link_loss.py
"""
import json
import socket
import sys
import threading
import time

from tactical_telemetry_feed import (EARTH_M_PER_DEG_LAT, STALE_AFTER_S,
                                     TelemetryFeed, flat_dist_m)
from udp_position_sender import PositionSim

TEST_PORT = 8898  # tranh xung port 8888 san xuat (8899 da cho test_telemetry_chain)
SOLDIER = (21.0333, 105.7333)
ALLY_START = (21.0333 + 20 / EARTH_M_PER_DEG_LAT, 105.7333)  # +20m Bac, di Dong 1.4 m/s


def send(tx, lat, lon, port=TEST_PORT):
    tx.sendto(json.dumps({"id": "ally-1", "lat": lat, "lon": lon,
                          "t": time.time()}).encode(), ("127.0.0.1", port))


def main():
    failures = []

    def check(name, cond, detail=""):
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")
        if not cond:
            failures.append(name)

    feed = TelemetryFeed(port=TEST_PORT, host="127.0.0.1").start()
    time.sleep(0.3)

    # Sender trong thread: goi 1Hz, luu ground truth theo thoi diem gui
    sim = PositionSim(ALLY_START[0], ALLY_START[1], bearing_deg=90.0, speed_mps=1.4)
    stop = threading.Event()
    sent = []  # (t_send, lat, lon)

    def run_sender():
        tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while not stop.is_set():
            now = time.time()
            lat, lon = sim.position_at(now)
            sent.append((now, lat, lon))
            send(tx, lat, lon)
            time.sleep(1.0)
        tx.close()

    th = threading.Thread(target=run_sender, daemon=True)
    th.start()

    # --- A) link song: nhan ~1Hz + toa do khop ground truth ---
    print("[A] Link song 3.2s...")
    time.sleep(3.2)
    pos = feed.fresh("ally-1")
    check("A: feed nhan position tu node", pos is not None, f"{pos}")
    if pos:
        # goi gan nhat voi vi tri feed dang giu — tranh race 1 cycle (1s) khi server nong
        gt = min(sent, key=lambda s: flat_dist_m(pos[0], pos[1], s[1], s[2]))
        err = flat_dist_m(pos[0], pos[1], gt[1], gt[2])
        check("A: toa do khop ground truth <1m", err < 1.0, f"(sai {err * 1000:.0f}mm)")
    check("A: node phat ~1Hz (3.2s → 3-4 goi)", 3 <= len(sent) <= 4,
          f"({len(sent)} goi)")

    # --- B) cat link: dung sender → stale <=5s, feed khong crash ---
    print("[B] Cat link (dung sender)...")
    stop.set()
    th.join(timeout=2)
    t0 = time.time()
    while feed.fresh("ally-1") is not None:
        if time.time() - t0 > STALE_AFTER_S + 2:  # an toan, tranh vo han
            break
        time.sleep(0.1)
    stale_after = time.time() - t0
    check("B: mat tin hieu sau khi cat link", feed.fresh("ally-1") is None)
    check("B: stale trong vong 5s (STALE_AFTER_S)",
          3.5 <= stale_after <= STALE_AFTER_S + 0.3, f"({stale_after:.1f}s)")
    check("B: relative_positions khong con ally",
          "ally-1" not in feed.relative_positions(SOLDIER))

    # --- C) khoi phuc: feed van song, nhan goi moi ---
    print("[C] Khoi phuc link...")
    tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    lat, lon = sim.position_at(time.time())
    send(tx, lat, lon)
    time.sleep(0.5)
    check("C: feed nhan lai goi moi (khong bi die sau cat link)",
          feed.fresh("ally-1") is not None)
    tx.close()
    feed.stop()

    if failures:
        print(f"\n{len(failures)} check THAT BAI: {failures}")
        sys.exit(1)
    print("\nTOAN BO CHECK PASS")


if __name__ == "__main__":
    main()
