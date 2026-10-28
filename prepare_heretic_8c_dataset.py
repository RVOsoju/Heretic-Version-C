"""Build the merged 8-class YOLO dataset (heretic-8c) from 4 pre-labeled sources.

Sources (all YOLO .txt labels):
  - MVRSD      dataset/mvrsl-military-vehicle/Filtered_MVD  -> military_vehicle (5 classes merged)
  - VisDrone   dataset/visdrone-vehicles-person             -> person, car, motorcycle, truck, bus
  - Mendeley   dataset/mendeley-uav-military/dataset        -> soldier, military_vehicle, person
  - COCO boat  dataset/coco-boat-subset                     -> boat (prepare_coco_boat_subset.py)

Output: dataset/heretic-8c/{train,val,test}/{images,labels} + heretic-8c.yaml
Images are symlinked (no disk duplication); labels are rewritten with mapped
class IDs. Excluded classes drop their label lines; an image left with no box
becomes an empty label file = negative sample (supplies "nothing to alert on").
Re-run safe: output dir is rebuilt from scratch.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dataset" / "heretic-8c"

# Target 8-class schema (locked 2026-10-15). boat(6) comes from the COCO subset.
CLASSES = ["person", "soldier", "car", "motorcycle", "truck", "bus", "boat", "military_vehicle"]

# tag -> base dir, split name map, {source class id: target class id}
SOURCES = {
    "mvrsd": {
        "base": ROOT / "dataset" / "mvrsl-military-vehicle" / "Filtered_MVD",
        "splits": {"train": "train", "val": "val", "test": "test"},
        # tank, truck, armored_vehicle, hummer, rocket_artillery -> military_vehicle
        "map": {0: 7, 1: 7, 2: 7, 3: 7, 4: 7},
    },
    "visdrone": {
        "base": ROOT / "dataset" / "visdrone-vehicles-person",
        "splits": {"train": "VisDrone2019-DET-train", "val": "VisDrone2019-DET-val",
                    "test": "VisDrone2019-DET-test-dev"},
        # pedestrian+people->person, car, truck, bus, motor->motorcycle;
        # bicycle/van/tricycle/awning-tricycle excluded
        "map": {0: 0, 1: 0, 3: 2, 5: 4, 8: 5, 9: 3},
    },
    "mendeley": {
        "base": ROOT / "dataset" / "mendeley-uav-military" / "dataset",
        "splits": {"train": "train", "val": "Val", "test": "test"},
        # tank->military_vehicle, people->person, soldier->soldier; drone excluded
        "map": {0: 7, 2: 0, 3: 1},
    },
    "coco": {
        "base": ROOT / "dataset" / "coco-boat-subset",
        "splits": {"train": "train", "val": "val", "test": "test"},
        # boat-only subset (single class 0) -> boat
        "map": {0: 6},
    },
}

IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


def remap_label(text: str, cmap: dict) -> str:
    """Rewrite class ids; drop lines of excluded classes and malformed lines."""
    kept = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        cls = int(parts[0])
        if cls in cmap:
            kept.append(f"{cmap[cls]} " + " ".join(parts[1:]))
    return "\n".join(kept)


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    per_split, per_class = {}, {i: 0 for i in range(len(CLASSES))}
    for tag, src in SOURCES.items():
        for split, src_split in src["splits"].items():
            img_dir = src["base"] / src_split / "images"
            lbl_dir = src["base"] / src_split / "labels"
            out_img, out_lbl = OUT / split / "images", OUT / split / "labels"
            out_img.mkdir(parents=True, exist_ok=True)
            out_lbl.mkdir(parents=True, exist_ok=True)
            n_img = 0
            for img_file in sorted(img_dir.iterdir()):
                if img_file.suffix.lower() not in IMAGE_EXTS:
                    continue
                lbl_file = lbl_dir / (img_file.stem + ".txt")
                if not lbl_file.exists():
                    continue
                name = f"{tag}__{img_file.name}"
                (out_img / name).symlink_to(img_file.resolve())
                label = remap_label(lbl_file.read_text(), src["map"])
                (out_lbl / f"{tag}__{img_file.stem}.txt").write_text(
                    label + "\n" if label else "")
                for line in label.splitlines():
                    per_class[int(line.split()[0])] += 1
                n_img += 1
            per_split[split] = per_split.get(split, 0) + n_img
            print(f"  {tag:9s} {split:5s}: {n_img} images")
    yaml_text = (
        "path: .\n"
        "train: train/images\n"
        "val: val/images\n"
        "test: test/images\n"
        f"nc: {len(CLASSES)}\n"
        f"names: {CLASSES}\n"
    )
    (OUT / "heretic-8c.yaml").write_text(yaml_text)
    print(f"\nTotal: {sum(per_split.values())} images | " +
          ", ".join(f"{CLASSES[i]}: {per_class[i]}" for i in range(len(CLASSES))))
    print(f"Output: {OUT}")


if __name__ == "__main__":
    build()
