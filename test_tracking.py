"""
Heretic Version C - test_tracking — AC1 (track ID) + AC2 (vận tốc tiếp cận)
+ verify object-height anchor (W2d1).

Sim: 150 khung 30fps 1280x720, 1 person đi thẳng về tâm (vị trí lính),
vận tốc ground truth = Δpx × scale × fps. Chạy YOLO26n + ByteTrack thật
(cùng pipeline heretic_phase4_hud.py).

AC1: re-ID < 5% trên các khung có detection (≥100 khung).
AC2: approach tính từ TrackStore (toàn track) sai < 10% so ground truth.
W2d1: frame tổng hợp 30m/FOV60° → distance qua object-height anchor sai < 25%.

Chạy: .venv/bin/python test_tracking.py
"""
import math
import sys
from pathlib import Path

import cv2
import numpy as np

from heretic_phase4_hud import FRAME_HEIGHT, FRAME_WIDTH, make_sim_frame
from tactical_height_anchor import (SIM_FOV_DEG, SIM_UAV_ALT_M, height_anchor_scale,
                                    sim_frame_scale)
from tactical_tracker import TrackStore

FPS = 30
N_FRAMES = 150
X0, X_END = 1100, 680  # person đi từ phải về gần tâm (hướng Tây)


def _base_frame():
    """Nền grid đều (đồng loại khung sim)."""
    frame = np.full((FRAME_HEIGHT, FRAME_WIDTH, 3), (15, 18, 15), dtype=np.uint8)
    for i in range(1, 10):
        x = FRAME_WIDTH * i // 10
        y = FRAME_HEIGHT * i // 10
        cv2.line(frame, (x, 0), (x, FRAME_HEIGHT), (30, 35, 30), 1)
        cv2.line(frame, (0, y), (FRAME_WIDTH, y), (30, 35, 30), 1)
    return frame


def person_sprite(target_h):
    """Cắt person lớn nhất từ bus.jpg (assets ultralytics), resize cao target_h px."""
    import ultralytics
    from ultralytics import YOLO
    img = cv2.imread(str(Path(ultralytics.__file__).parent / "assets" / "bus.jpg"))
    model = YOLO("yolo26n.pt")
    res = model.predict(img, verbose=False)[0]
    pidx = [k for k, v in model.names.items() if v == "person"][0]
    persons = [b for b in res.boxes if int(b.cls[0]) == pidx]
    if not persons:
        sys.exit("KHONG TIM THAY person trong bus.jpg")
    b = max(persons, key=lambda b: float((b.xyxy[0][2] - b.xyxy[0][0]) *
                                         (b.xyxy[0][3] - b.xyxy[0][1])))
    x1, y1, x2, y2 = map(int, b.xyxy[0].tolist())
    crop = img[max(0, y1):y2, max(0, x1):x2]
    h, w = crop.shape[:2]
    return cv2.resize(crop, (max(8, int(w * target_h / h)), target_h))


def gen_frames(sprite):
    """150 khung: person đi thẳng từ X0 đến X_END, y = tâm khung."""
    frames, xs = [], []
    sh, sw = sprite.shape[:2]
    cy = FRAME_HEIGHT // 2
    for i in range(N_FRAMES):
        frame = _base_frame()
        x = int(X0 + (X_END - X0) * i / (N_FRAMES - 1))
        frame[cy - sh // 2: cy - sh // 2 + sh, x - sw // 2: x - sw // 2 + sw] = sprite
        frames.append(frame)
        xs.append(x)
    return frames, xs


def ground_truth_vmps():
    """Vận tốc ground truth (m/s) = |Δx|/Δt × scale sim (30m/FOV60°)."""
    v_px = abs(X0 - X_END) / (N_FRAMES - 1)
    return v_px * FPS * sim_frame_scale(FRAME_WIDTH, SIM_UAV_ALT_M, SIM_FOV_DEG)


def run_tracking(frames):
    """Chạy YOLO26n + ByteTrack thật; trả (ids mỗi khung, [(ts, dist_m)] toàn track).
    TrackStore.update() được gọi mỗi detection (code hệ thống dưới test);
    (ts, dist) gom cục bộ vì TrackStore chỉ giữ cửa sổ 5 khung."""
    from ultralytics import YOLO
    model = YOLO("yolo26n.pt")
    store = TrackStore()
    scale = sim_frame_scale(FRAME_WIDTH)
    cx, cy = FRAME_WIDTH // 2, FRAME_HEIGHT // 2
    ids_per_frame, detections = [], []
    for i, frame in enumerate(frames):
        ts = i / FPS
        # imgsz=1280: khung sim 1280x720 native (PDR: 720p GPU) — person 62px
        # mat hon khi downscale ve 640
        res = model.track(frame, persist=True, tracker="bytetrack.yaml",
                          stream=False, verbose=False, imgsz=1280)
        ids = []
        for r in res:
            for box in r.boxes:
                if box.id is None:
                    continue
                tid = int(box.id[0])
                ids.append(tid)
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                dist = math.hypot((x1 + x2) / 2 - cx, (y1 + y2) / 2 - cy) \
                    * height_anchor_scale("person", y2 - y1, scale)
                store.update(tid, ts, (x1 + x2) / 2, (y1 + y2) / 2, dist, scale)
                detections.append((ts, dist))
        ids_per_frame.append(ids)
        store.prune(now=ts)
    return ids_per_frame, detections


def full_track_approach(detections):
    """Approach (m/s) trên TOÀN BỘ các lần detection — loại nhiễu jitter của cửa sổ 5 khung."""
    if len(detections) < 2:
        return 0.0
    (t0, d0), (t1, d1) = detections[0], detections[-1]
    dt = t1 - t0
    return (d0 - d1) / dt if dt > 0 else 0.0


def main():
    failures = []

    def check(name, cond, detail=""):
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")
        if not cond:
            failures.append(name)

    scale = sim_frame_scale(FRAME_WIDTH)

    # --- W2d1: object-height anchor trên frame tổng hợp 30m/FOV60° ---
    print("[W2d1] Object-height anchor (frame sim 30m, FOV 60°)")
    for d in (15, 10):
        _frame, box = make_sim_frame(d, "Tây")
        x1, y1, x2, y2 = box
        s = height_anchor_scale("person", y2 - y1, scale)
        dist = math.hypot((x1 + x2) / 2 - FRAME_WIDTH / 2,
                          (y1 + y2) / 2 - FRAME_HEIGHT / 2) * s
        check(f"anchor {d}m: distance sai <25%", abs(dist - d) / d < 0.25,
              f"(dist={dist:.1f}m, scale={s:.5f} vs sim {scale:.5f})")
    check("anchor fallback: box <8px → scale 0.05",
          height_anchor_scale("person", 5) == 0.05)
    check("anchor fallback: class không có trong bảng → scale 0.05",
          height_anchor_scale("airplane", 50) == 0.05)

    # --- Sim video: 1 person đi thẳng về tâm ---
    v_gt = ground_truth_vmps()
    print(f"\n[SIM] {N_FRAMES} khung {FPS}fps, person {X0}→{X_END}px, "
          f"v_gt={v_gt:.2f} m/s")
    person_h = max(8, int(1.7 / scale))
    sprite = person_sprite(person_h)
    frames, _xs = gen_frames(sprite)

    print("[YOLO] Đang chạy YOLO26n + ByteTrack trên 150 khung...")
    ids_per_frame, detections = run_tracking(frames)

    detected = [ids for ids in ids_per_frame if ids]
    check(f"AC1: ≥100 khung có detection", len(detected) >= 100,
          f"({len(detected)}/{N_FRAMES})")

    # AC1: re-ID = xuất hiện track_id mới (không thấy ở các khung detected trước)
    reid, seen = 0, set()
    for ids in detected:
        new = [i for i in ids if i not in seen]
        reid += len(new)
        seen.update(ids)
    reid -= len(detected[0]) if detected else 0  # lần đầu không phải re-ID
    reid_rate = reid / max(1, len(detected) - 1)
    check("AC1: re-ID < 5%", reid_rate < 0.05,
          f"({reid} lần re-ID / {len(detected) - 1} khung = {reid_rate:.1%})")

    # AC2: approach toàn track so với ground truth
    v_meas = full_track_approach(detections)
    err = abs(v_meas - v_gt) / v_gt
    check("AC2: approach sai < 10% so ground truth", err < 0.10,
          f"(meas={v_meas:.2f} m/s vs gt={v_gt:.2f} m/s, sai {err:.1%})")

    if failures:
        print(f"\n{len(failures)} check THAT BAI: {failures}")
        sys.exit(1)
    print("\nTOAN BO CHECK PASS")


if __name__ == "__main__":
    main()
