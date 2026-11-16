"""
Heretic Version C - Export weight YOLO sang TensorRT (.engine) de tang FPS.

QUAN TRONG: file .engine CHUNG KY theo kien truc GPU + phien ban TensorRT.
Engine xay tren server (RTX 5000 Ada) KHONG chay duoc tren laptop (RTX 3050 Ampere).
→ Chay script nay TRÊN MÁY SẼ CHẠY HUD (laptop), rói truyên --model .engine.

Cai dat (chay 1 lan trên laptop):
  .venv/bin/pip install tensorrt onnx onnxslim

Chay:
  .venv/bin/python export_trt_engine.py \
      --weight weights/yolo26s-military-8c-k2.pt \
      --out weights/yolo26s-military-8c-k2.engine \
      --imgsz 640 --half

Sau dó chay HUD (ByteTrack giu nguyen — tracking la post-inference, doc lap backend):
  .venv/bin/python heretic_phase4_hud.py --model weights/yolo26s-military-8c-k2.engine --fp16
"""

import argparse

from ultralytics import YOLO


def main():
    p = argparse.ArgumentParser(description="Export YOLO .pt -> TensorRT .engine (tang FPS)")
    p.add_argument("--weight", required=True, help="Duong dan .pt goc")
    p.add_argument("--out", required=True, help="Duong dan .engine xu")
    p.add_argument("--imgsz", type=int, default=640, help="Kich thuoc input (mac dinh 640)")
    p.add_argument("--half", action="store_true",
                   help="FP16 — tang FPS, khuyen nghi")
    p.add_argument("--device", type=int, default=0, help="GPU index (mac dinh 0)")
    p.add_argument("--dynamic", action="store_true",
                   help="Dynamic batch/size (build chet, lanh hon; mac dinh OFF)")
    a = p.parse_args()

    print(f"[INFO] Export {a.weight} -> {a.out} "
          f"(imgsz={a.imgsz}, half={a.half}, device={a.device}, dynamic={a.dynamic})")
    model = YOLO(a.weight)
    model.export(format="engine", imgsz=a.imgsz, half=a.half,
                 device=a.device, dynamic=a.dynamic, batch=1)
    print(f"[XONG] {a.out}")
    print("Chay HUD: .venv/bin/python heretic_phase4_hud.py --model "
          f"{a.out} --fp16   (ByteTrack giu nguyen)")


if __name__ == "__main__":
    main()
