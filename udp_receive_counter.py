"""
Heretic Version C - Dem goi UDP 1Hz trong N giay (bench packet loss)

Chay tren laptop, dong thoi voi udp_position_sender (1Hz).
KHONG chay HUD cung luc — HUD da bind port 8888.

Chay (laptop):
  .venv\\Scripts\\python udp_receive_counter.py --duration 30
"""
import argparse
import socket
import time

from tactical_telemetry_feed import TELEMETRY_PORT


def main():
    parser = argparse.ArgumentParser(description="Dem goi UDP 1Hz — bench packet loss")
    parser.add_argument("--duration", type=float, default=30.0,
                        help="so giay dem (mac dinh 30)")
    parser.add_argument("--port", type=int, default=TELEMETRY_PORT,
                        help=f"port UDP (mac dinh {TELEMETRY_PORT})")
    args = parser.parse_args()

    rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rx.bind(("", args.port))
    rx.settimeout(0.5)
    t0 = time.time()
    n = 0
    while time.time() - t0 < args.duration:
        try:
            rx.recvfrom(2048)
            n += 1
        except socket.timeout:
            pass
    total = time.time() - t0
    expected = total  # sender 1Hz → mong đợi ~1 goi/giay
    loss = max(0.0, 100.0 * (1.0 - n / expected)) if expected > 0 else 0.0
    print(f"[COUNT] nhan {n}/{expected:.0f} goi trong {total:.0f}s — "
          f"packet loss {loss:.1f}% (ngưỡng ~0)")
    rx.close()


if __name__ == "__main__":
    main()
