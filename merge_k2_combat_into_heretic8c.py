"""Append the K2 combat-labeling set (soldier + military_vehicle) to heretic-8c.

Run AFTER prepare_heretic_8c_dataset.py (which rebuilds heretic-8c from the 4
original sources with car/person downsampling). K2 is pure soldier/mil-vehicle,
so the dominant-class downsampling does not apply to it.

- Remaps K2 class ids -> heretic-8c: 0 (military_vehicle) -> 7, 1 (soldier) -> 1.
- Seeded 85/15 split: 85% -> heretic-8c/train (augments training),
  15% -> heretic-8c/domainval-k2 (a SEPARATE domain-matched val set for
  measuring OOD recall on combat footage, kept out of the in-domain val).
- Images symlinked (no disk duplication); labels rewritten with remapped ids.
- Prefixes every K2 file with k2_ (no name collision); idempotent (clears
  prior k2_* before re-adding).
"""
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HERETIC = ROOT / "dataset" / "heretic-8c"
K2 = ROOT / "dataset" / "k2-combat-labeling" / "train"

# K2 id -> heretic-8c id (heretic-8c: person=0 soldier=1 ... military_vehicle=7)
ID_MAP = {0: 7, 1: 1}
HERETIC_NAMES = ['person', 'soldier', 'car', 'motorcycle', 'truck', 'bus', 'boat', 'military_vehicle']
SEED = 0
VAL_FRAC = 0.15
PREFIX = "k2_"


def remap_label_lines(text: str) -> list:
    """Rewrite class ids via ID_MAP; drop malformed lines; return new lines."""
    out = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        parts[0] = str(ID_MAP[int(parts[0])])
        out.append(" ".join(parts))
    return out


def main() -> None:
    imgs = sorted((K2 / "images").glob("*.jpg"))
    lab_dir = K2 / "labels"
    print(f"K2 source: {len(imgs)} images")
    assert len(imgs) > 0, "no K2 images found"

    # Seeded 85/15 split (reproducible)
    random.Random(SEED).shuffle(imgs)
    n_val = int(len(imgs) * VAL_FRAC)
    val_set, train_set = imgs[:n_val], imgs[n_val:]
    print(f"split (seed={SEED}): {len(train_set)} train + {len(val_set)} domain-val")

    # Idempotency: clear prior k2_* in both destinations before re-adding
    dests = [HERETIC / "train" / "images", HERETIC / "train" / "labels",
             HERETIC / "domainval-k2" / "images", HERETIC / "domainval-k2" / "labels"]
    for d in dests:
        d.mkdir(parents=True, exist_ok=True)
        for old in d.glob(PREFIX + "*"):
            old.unlink()

    def place(img: Path, d_img: Path, d_lab: Path) -> None:
        (d_img / (PREFIX + img.name)).symlink_to(img.resolve())
        lab = lab_dir / (img.stem + ".txt")
        lines = remap_label_lines(lab.read_text()) if lab.exists() else []
        (d_lab / (PREFIX + img.stem + ".txt")).write_text("\n".join(lines) + ("\n" if lines else ""))

    for img in train_set:
        place(img, HERETIC / "train" / "images", HERETIC / "train" / "labels")
    for img in val_set:
        place(img, HERETIC / "domainval-k2" / "images", HERETIC / "domainval-k2" / "labels")

    # Domain-val yaml: same 8-class schema, only soldier+mil-vehicle present.
    (HERETIC / "domainval-k2.yaml").write_text(
        f"path: {HERETIC.resolve().as_posix()}\n"
        "val: domainval-k2/images\n"
        f"nc: {len(HERETIC_NAMES)}\n"
        f"names: {HERETIC_NAMES}\n"
    )
    print(f"wrote {HERETIC / 'domainval-k2.yaml'}")
    print("DONE: K2 merged into heretic-8c/train + domainval-k2/")


if __name__ == "__main__":
    main()
