"""Render a YOLO detection-overlay video: run a weight over a source clip and
write box+label overlays to an mp4, to visually inspect detection quality on
the K2 combat clips. Output is regenerable (gitignored under assets/k2-*.mp4).

Alert classes (soldier / military_vehicle) draw green; everything else orange,
so the threat-relevant detections stand out at a glance.

Usage:
  python render_yolo_detect_video.py --source assets/k2-soledar-720p.mp4 \
      --model weights/yolo26s-military-8c-k2-cp.pt \
      --out assets/k2-soledar-720p-cp-detect.mp4
"""
import argparse

import cv2
from ultralytics import YOLO

ALERT_CLASSES = ("soldier", "military_vehicle")
COL_ALERT = (0, 200, 0)     # green  (BGR)
COL_OTHER = (0, 165, 255)   # orange (BGR)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, help="input video (mp4)")
    p.add_argument("--model", required=True, help="YOLO weight (.pt)")
    p.add_argument("--out", required=True, help="output video (mp4)")
    p.add_argument("--conf", type=float, default=0.35, help="min confidence")
    p.add_argument("--device", type=str, default="0", help="cuda device / cpu")
    p.add_argument("--max-frames", type=int, default=0, help="0 = all frames")
    args = p.parse_args()

    model = YOLO(args.model)
    cap = cv2.VideoCapture(args.source)
    if not cap.isOpened():
        raise SystemExit(f"Cannot open source video: {args.source}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # mp4v (MPEG-4) is reliably encodable by OpenCV's bundled ffmpeg; h264
    # (avc1) is often absent, so keep the render portable and re-encode later.
    writer = cv2.VideoWriter(args.out, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

    n = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        res = model(frame, verbose=False, conf=args.conf, device=args.device)[0]
        for b in res.boxes:
            x1, y1, x2, y2 = (int(v) for v in b.xyxy[0])
            name = model.names[int(b.cls[0])]
            conf = float(b.conf[0])
            col = COL_ALERT if name in ALERT_CLASSES else COL_OTHER
            cv2.rectangle(frame, (x1, y1), (x2, y2), col, 2)
            cv2.putText(frame, f"{name} {conf:.2f}", (x1, max(0, y1 - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 1, cv2.LINE_AA)
        writer.write(frame)
        n += 1
        if n % 500 == 0:
            print(f"  {n} frames ...", flush=True)
        if args.max_frames and n >= args.max_frames:
            break
    cap.release()
    writer.release()
    print(f"Wrote {n} frames -> {args.out}")


if __name__ == "__main__":
    main()
