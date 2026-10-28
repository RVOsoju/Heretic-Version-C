"""Build a COCO-2017 boat-only YOLO subset (single class, id 0) for heretic-8c.

COCO is the only local source for the boat class (class 6 in the 8-class
schema). We extract ONLY images that contain at least one boat box and write
boat-only labels — other COCO classes are irrelevant here (YAGNI) and the
merged dataset gets them from VisDrone.

Inputs (expected under /tmp/coco, re-download if missing):
  - /tmp/coco/annotations/instances_train2017.json
  - /tmp/coco/train2017.zip

Output: dataset/coco-boat-subset/{train,val,test}/{images,labels}
Deterministic 80/10/10 split (image_id order, index % 10). Labels always end
with a trailing newline. Re-run safe: output dir is rebuilt from scratch.
The merge step lives in prepare_heretic_8c_dataset.py (source tag "coco").
"""
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dataset" / "coco-boat-subset"
ANN_JSON = Path("/tmp/coco/annotations/instances_train2017.json")
IMG_ZIP = Path("/tmp/coco/train2017.zip")
BOAT_CAT_ID = 9  # COCO category id for "boat" (verified in instances JSON)


def load_boat_boxes() -> dict:
    """Return {file_name: [(cx, cy, w, h) normalized, ...]} for boat images."""
    with open(ANN_JSON) as f:
        coco = json.load(f)
    sizes = {im["id"]: (im["width"], im["height"]) for im in coco["images"]}
    names = {im["id"]: im["file_name"] for im in coco["images"]}
    boxes: dict = {}
    for ann in coco["annotations"]:
        if ann["category_id"] != BOAT_CAT_ID or ann.get("iscrowd"):
            continue
        w, h = sizes[ann["image_id"]]
        x, y, bw, bh = ann["bbox"]
        cx, cy = (x + bw / 2) / w, (y + bh / 2) / h
        boxes.setdefault(names[ann["image_id"]], []).append(
            (cx, cy, bw / w, bh / h)
        )
    return boxes


def assign_split(rank: int) -> str:
    """Deterministic 80/10/10: 0-7 train, 8 val, 9 test."""
    return ("train", "train", "train", "train", "train",
            "train", "train", "train", "val", "test")[rank % 10]


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    boat = load_boat_boxes()
    file_names = sorted(boat)
    wanted = {f"train2017/{name}" for name in file_names}
    per_split = {"train": 0, "val": 0, "test": 0}
    per_box = 0
    with zipfile.ZipFile(IMG_ZIP) as zf:
        for rank, name in enumerate(file_names):
            split = assign_split(rank)
            img_dir, lbl_dir = OUT / split / "images", OUT / split / "labels"
            img_dir.mkdir(parents=True, exist_ok=True)
            lbl_dir.mkdir(parents=True, exist_ok=True)
            with zf.open(f"train2017/{name}") as src, open(
                img_dir / name, "wb"
            ) as dst:
                shutil.copyfileobj(src, dst)
            lines = [
                f"0 {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}"
                for cx, cy, bw, bh in boat[name]
            ]
            (lbl_dir / (Path(name).stem + ".txt")).write_text(
                "\n".join(lines) + "\n"
            )
            per_split[split] += 1
            per_box += len(lines)
    print(f"Total: {sum(per_split.values())} images, {per_box} boat boxes | "
          + ", ".join(f"{k}: {v}" for k, v in per_split.items()))
    print(f"Output: {OUT}")


if __name__ == "__main__":
    build()
