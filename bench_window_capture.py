"""
Heretic Version C - Bench capture window mirror (UxPlay/scrcp) — Windows only

Do fps thuc + kich thuoc khung khi capture window mirror, chay dong thoi voi
sender UDP 8888 (dien tuyen demo). Ngưỡng: ≥15fps on dinh.

Chay (laptop, da co window mirror mo):
  .venv/bin/python bench_window_capture.py --title UxPlay --duration 10
  .venv/bin/python bench_window_capture.py --title scrcp --duration 30
  .venv/bin/python bench_window_capture.py --list   # xem title thuc cua cac window
"""
import argparse
import time

from tactical_video_source import WindowSource


def main():
    parser = argparse.ArgumentParser(
        description="Bench capture window mirror (fps + kich thuoc khung)")
    parser.add_argument("--title", default="UxPlay",
                        help="substring cua title window (mac dinh: UxPlay)")
    parser.add_argument("--duration", type=float, default=10.0,
                        help="so giay capture (mac dinh 10)")
    parser.add_argument("--list", action="store_true",
                        help="in danh sach title cua cac window hien thi (de tim title) va thoat")
    args = parser.parse_args()

    if args.list:
        from tactical_video_source import list_visible_window_titles
        print("[BENCH] cac window hien thi (tim title UxPlay/scrcp trong danh sach):")
        for t in list_visible_window_titles():
            print(f"  {t}")
        return

    try:
        src = WindowSource(args.title)
    except RuntimeError as e:
        print(f"[BENCH] {e}")
        print("[BENCH] chay lai voi --list de xem title thuc cua window mirror")
        return
    t0 = time.time()
    frames, size = 0, None
    print(f"[BENCH] capture window chua '{args.title}' trong {args.duration:.0f}s...")
    while time.time() - t0 < args.duration:
        ok, frame = src.read()
        if not ok:
            break
        frames += 1
        size = f"{frame.shape[1]}x{frame.shape[0]}"
        if frames % 30 == 0:
            print(f"  t={time.time() - t0:5.1f}s fps={frames / (time.time() - t0):5.1f}")
    total = time.time() - t0
    print(f"[BENCH] {frames} khung / {total:.1f}s = {frames / total:.1f}fps "
          f"(ngưỡng ≥15), kich thuoc {size}")
    src.release()
    print("[BENCH] DONE")


if __name__ == "__main__":
    main()
