"""
Heretic Version C - B6 bước 1: chat luong detection 360P

Tao video 640×360 (30 khung @30fps) tu bus.jpg cua ultralytics: anh duoc dat
len canvas 1280×720, khung hinh 640×360 pan ngang -> mo phong camera UAV
360P. GT = box yolo26n tren canvas 720p (bien anh affine cung tham so pan).

Log: precision/recall moi khung (IoU >= 0.3), conf trung binh, chieu cao
box person (px) -> so lieu de ghi vao register diem mu B6 (plan.md).

Chay:
  python test_360p_precision.py
"""

import os

import cv2
import numpy as np
from ultralytics import YOLO

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
CANVAS_JPG = os.path.join(ASSETS, "bus-720p-canvas.jpg")
VIDEO_MP4 = os.path.join(ASSETS, "bus-360p.mp4")
W, H = 640, 360
N_FRAMES = 30
FPS = 30
CONF_MIN = 0.25
IOU_MATCH = 0.3


def build_canvas():
    """bus.jpg (810x1080) thu nho dat gan giua canvas 1280x720. Tra ve canvas."""
    import ultralytics
    src = os.path.join(os.path.dirname(ultralytics.__file__), "assets", "bus.jpg")
    img = cv2.imread(src)
    h_new = 420
    w_new = int(img.shape[1] * h_new / img.shape[0])
    img = cv2.resize(img, (w_new, h_new))
    canvas = np.full((720, 1280, 3), (120, 130, 120), dtype=np.uint8)
    y0, x0 = (720 - h_new) // 2, (1280 - w_new) // 2
    canvas[y0:y0 + h_new, x0:x0 + w_new] = img
    cv2.imwrite(CANVAS_JPG, canvas)
    return canvas


def make_video(canvas):
    """Khung 640×360 pan ngang (x: 0 -> 640, y: 180) -> luu mp4. Tra offsets."""
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(VIDEO_MP4, fourcc, FPS, (W, H))
    offsets = []
    for i in range(N_FRAMES):
        x0 = int(640 * i / (N_FRAMES - 1))
        y0 = 180
        writer.write(canvas[y0:y0 + H, x0:x0 + W])
        offsets.append((x0, y0))
    writer.release()
    return offsets


def iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    union = (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - inter
    return inter / union if union > 0 else 0.0


def main():
    canvas = build_canvas()
    offsets = make_video(canvas)

    model = YOLO("yolo26n.pt")

    # GT: box model tren canvas 720p (conf >= 0.25)
    gt = model(CANVAS_JPG, verbose=False)[0].boxes
    gt_boxes = []
    for b in gt:
        if float(b.conf[0]) >= CONF_MIN:
            gt_boxes.append((int(b.cls[0]), [float(v) for v in b.xyxy[0].tolist()],
                             float(b.conf[0])))
    print(f"[GT] Canvas 720p: {len(gt_boxes)} box (conf >= {CONF_MIN})")
    for cls, box, conf in gt_boxes:
        print(f"      {model.names[int(cls)]} conf={conf:.2f} box_h={box[3]-box[1]:.0f}px")

    cap = cv2.VideoCapture(VIDEO_MP4)
    rows = []
    for i in range(N_FRAMES):
        ok, frame = cap.read()
        if not ok:
            break
        x0, y0 = offsets[i]
        gt_win = [(c, [v - (x0 if k % 2 == 0 else y0) for k, v in enumerate(box)], conf)
                  for c, box, conf in gt_boxes]
        gt_win = [g for g in gt_win
                  if -40 <= g[1][0] <= W + 40 and -40 <= g[1][1] <= H + 40]
        res = model(frame, verbose=False, conf=CONF_MIN)[0].boxes
        det = [(int(b.cls[0]), [float(v) for v in b.xyxy[0].tolist()], float(b.conf[0]))
               for b in res]
        matched_gt = set()
        tp = fp = 0
        for c, box, conf in det:
            hit = next((j for j in range(len(gt_win)) if j not in matched_gt
                        and gt_win[j][0] == c and iou(box, gt_win[j][1]) >= IOU_MATCH), None)
            if hit is not None:
                matched_gt.add(hit)
                tp += 1
            else:
                fp += 1
        fn = len(gt_win) - len(matched_gt)
        precision = tp / (tp + fp) if tp + fp else 1.0
        recall = tp / (tp + fn) if tp + fn else 1.0
        person_h = [box[3] - box[1] for c, box, _ in det
                    if model.names[c] in ("person",)]
        rows.append((i, len(det), tp, fp, fn, precision, recall,
                     f"{np.mean(person_h):.0f}" if person_h else "-"))
    cap.release()

    print(f"\n{'#':>3} {'det':>3} {'TP':>2} {'FP':>2} {'FN':>2} "
          f"{'P':>5} {'R':>5}  person_h(px)")
    for r in rows:
        print(f"{r[0]:>3} {r[1]:>3} {r[2]:>2} {r[3]:>2} {r[4]:>2} "
              f"{r[5]:>5.2f} {r[6]:>5.2f}  {r[7]:>8}")
    p_all = np.mean([r[5] for r in rows])
    r_all = np.mean([r[6] for r in rows])
    print(f"\n[B6-360P] precision tb = {p_all:.2f}, recall tb = {r_all:.2f} "
          f"({N_FRAMES} khung 640×360, yolo26n, conf >= {CONF_MIN})")
    print(f"[B6-360P] Video: {VIDEO_MP4}, canvas: {CANVAS_JPG}")


if __name__ == "__main__":
    main()
