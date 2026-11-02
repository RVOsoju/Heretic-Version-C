"""Fine-tune yolo26n to the 8-class heretic schema on the server, then validate.

Dataset = dataset/heretic-8c (built by prepare_heretic_8c_dataset.py). Trains
overnight on the server with two GPUs, copies the best weight to
weights/yolo26n-military-8c.pt, then prints overall + per-class mAP.

Class imbalance (car ~187k boxes vs soldier ~3.4k) is NOT pre-weighted: YOLO's
per-box loss is robust to moderate imbalance, so we train as-is and read the
per-class mAP below. If soldier mAP is the weak spot, iterate in W4 (raise
epochs / oversample soldier) rather than pre-tuning blindly.

Usage (server):
  python train_military_yolo.py --base yolo26n.pt --epochs 100 --device 0,3
  python train_military_yolo.py --base yolo26s.pt --epochs 100 --device 0,3
  python train_military_yolo.py --epochs 50 --batch 32
  python train_military_yolo.py --val-only          # validate an existing weight
"""
import argparse
import shutil
from pathlib import Path

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent
DATA_YAML = ROOT / "dataset" / "heretic-8c" / "heretic-8c.yaml"
OUT_DIR = ROOT / "weights"


def run_name_for(base: str) -> str:
    # yolo26n.pt -> yolo26n-military-8c, yolo26s.pt -> yolo26s-military-8c
    return f"{Path(base).stem}-military-8c"


def train(args, base_path: Path, run_name: str, final_weight: Path) -> Path:
    model = YOLO(str(base_path))
    model.train(
        data=str(DATA_YAML),
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=args.device,
        project=str(OUT_DIR),
        name=run_name,
        exist_ok=True,
        seed=0,
        mosaic=args.mosaic,
        mixup=args.mixup,
        copy_paste=args.copy_paste,  # synthesize extra instances of rare classes
        close_mosaic=args.close_mosaic,  # disable mosaic in the final N epochs
    )
    best = OUT_DIR / run_name / "weights" / "best.pt"
    shutil.copyfile(best, final_weight)
    print(f"Best weight copied to: {final_weight}")
    return final_weight


def validate(args, weight: Path) -> None:
    model = YOLO(str(weight))
    results = model.val(data=str(DATA_YAML), split="val", imgsz=args.imgsz,
                        device=args.device)
    print(f"mAP50: {results.box.map50:.4f}   mAP50-95: {results.box.map:.4f}")
    print("Per-class mAP50-95:")
    maps = results.box.maps  # np.ndarray indexed by class id
    for cid, name in model.names.items():
        print(f"  {name:18s} {maps[cid]:.4f}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--epochs", type=int, default=30)
    p.add_argument("--batch", type=int, default=64)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--device", type=str, default="0,1")
    p.add_argument("--mosaic", type=float, default=1.0)
    p.add_argument("--mixup", type=float, default=0.0)
    p.add_argument("--copy-paste", type=float, default=0.0,
                   help="copy-paste ratio (synthesizes rare-class instances)")
    p.add_argument("--close-mosaic", type=int, default=10)
    p.add_argument("--val-only", action="store_true")
    p.add_argument("--model", type=str, default=None,
                   help="weight to validate with --val-only (default: final weight)")
    p.add_argument("--base", type=str, default="yolo26n.pt",
                   help="pretrained base model (yolo26n.pt / yolo26s.pt); "
                        "run name + final weight derive from its stem")
    args = p.parse_args()

    if not DATA_YAML.exists():
        raise SystemExit(f"Missing {DATA_YAML} — run prepare_heretic_8c_dataset.py first")

    run_name = run_name_for(args.base)
    final_weight = OUT_DIR / f"{run_name}.pt"

    if args.val_only:
        weight = Path(args.model) if args.model else final_weight
    else:
        weight = train(args, ROOT / args.base, run_name, final_weight)
    validate(args, weight)


if __name__ == "__main__":
    main()
