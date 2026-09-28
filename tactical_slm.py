"""
Heretic Version C - Phase 3: Tro ly Chien thuat SLM (Ollama local)

Doc JSON tu Phase 2 (stdin: moi payload la mot JSON object, hoac --demo)
va in ra DUY NHAT mot cau canh bao chien thuat ngan bang tieng Viet.

Ngat ngan canh bao (dinh, khong do SLM quyet dinh):
  - Phan phuong tien/binh lanh (target nguy hiem) < 100m: khoi dau canh bao
  - Moi giam 10m khoang cach: canh bao mot lan
  - Duoi 10m: moi giam 1m canh bao mot lan

Chay:
  python tactical_slm.py --demo
  python heretic_phase2.py | python tactical_slm.py
  echo '{"soldier_gps":{},"detected_threats":[{"target":"person","distance_m":95,"bearing":"Tay"}]}' | python tactical_slm.py
"""

import json
import os
import sys
import time

import requests

# Duoc phong qua env OLLAMA_HOST (vi du http://localhost:11435 cho GPU server rieng)
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_URL = f"{OLLAMA_HOST}/api/generate"
MODEL = "qwen2.5:3b"

# Chi can bao cac loai target mat (binh lanh + phuong tien)
DANGEROUS_TARGETS = {"person", "car", "motorcycle", "truck", "bus", "boat"}

# System prompt thiet ke cho SLM 3B: vai tro ro, luat rat ngan,
# gan example de giam token output -> phan ung nhanh.
SYSTEM_PROMPT = """Ban la He thong Canh bao Chien thuat cua mot quan doi.
Doc JSON cam bien va tra ve DUY NHAT 1 cau canh bao bang tieng Viet, toi da 12 tu, bat dau bang "CANH BAO:".
- Chi lay target NGUY HIEM NHAT ( khoang cach gan nhat ) trong danh sach.
- Chi tinh den target: person, car, motorcycle, truck, bus, boat.
- person -> "Ke dich"; car/motorcycle -> "xe dich"; truck/bus -> "xe tai dich".
- Neu khong co target nguy hiem: tra ve "An toan".
- Khong giai thich, khong them dong khac, khong markdown.
Vi du: CANH BAO: Ke dich cach 12m huong Dong!"""


class TacticalAlertGater:
    """Ngat ngan canh bao theo khoang cach: <100m khoi dau, moi -10m bao, duoi 10m moi -1m bao."""

    def __init__(self, warn_range=100.0, step=10.0, close_range=10.0, close_step=1.0):
        self.warn_range = warn_range
        self.step = step
        self.close_range = close_range
        self.close_step = close_step
        self.last_warned = {}  # (target, bearing) -> khoang cach lan bao gan nhat

    @staticmethod
    def _key(threat):
        return (threat.get("target"), threat.get("bearing"))

    def should_alert(self, threat):
        """Tra ve True neu threat nay de duoc canh bao o lan nay."""
        distance = float(threat.get("distance_m", float("inf")))
        key = self._key(threat)
        if distance >= self.warn_range:
            self.last_warned.pop(key, None)  # ra ngoai do -> reset de bao lai khi tiep can
            return False
        prev = self.last_warned.get(key)
        if prev is None:
            return True  # lan phat hien dau tien trong do
        step = self.close_step if distance < self.close_range else self.step
        return distance <= prev - step


def call_ollama(prompt, timeout=10.0):
    """Goi Ollama, tra ve (cau tra loi, latency_ms). Tun tuoc do de dam bao < 0.2s."""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "30m",  # giu mo hinh nong tren GPU de cac lan goi sau nhanh
        "options": {
            "num_predict": 20,   # gi han so token output -> nhanh
            "temperature": 0.0,  # greedy: xac dinh toan phan, tranh halucination huong
            "top_k": 1,
            "stop": ["\n"],      # chi phuc vu 1 dong duy nhat
        },
    }
    start = time.perf_counter()
    response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    latency_ms = (time.perf_counter() - start) * 1000
    response.raise_for_status()
    return response.json()["response"].strip(), latency_ms


def process_payload(payload, gater):
    """Xuly mot payload JSON: kiem ngat ngan -> goi SLM -> in cau canh bao."""
    threats = [
        t for t in payload.get("detected_threats", [])
        if t.get("target") in DANGEROUS_TARGETS
    ]
    alerting = [t for t in threats if gater.should_alert(t)]
    if not alerting:
        return
    # Ghi nhan khoang cach da bao (lay target gan nhat de SLM chon)
    closest = min(alerting, key=lambda t: float(t.get("distance_m", 1e9)))
    gater.last_warned[gater._key(closest)] = float(closest["distance_m"])

    prompt = SYSTEM_PROMPT + "\n\nDu lieu cam bien:\n" + json.dumps(payload, ensure_ascii=False)
    try:
        alert, latency_ms = call_ollama(prompt)
    except Exception as exc:
        print(f"[LOI] Khong the goi Ollama: {exc}", flush=True)
        return
    print(f"[{latency_ms:.0f}ms] {alert}", flush=True)


def iter_json_objects(text):
    """Parse cac JSON object lien tiep trong text (co the do, co the keo dan)."""
    decoder = json.JSONDecoder()
    idx = 0
    while True:
        brace = text.find("{", idx)
        if brace == -1:
            return
        try:
            obj, end = decoder.raw_decode(text, brace)
            yield obj
            idx = end
        except json.JSONDecodeError:
            idx = brace + 1


def run_demo(gater):
    """Demo: mot tinh binh tiep can tu 95m den 1m, mo hinh ngat ngan canh bao."""
    print("[DEMO] Binh lanh tiep can huong Tay: 95m -> 1m (Bam 'q'... chong 3s giua tung khung)", flush=True)
    for distance in [95, 90, 85, 75, 65, 55, 45, 35, 25, 15, 9, 8, 7, 5, 3, 1]:
        payload = {
            "soldier_gps": {"lat": 21.0333, "lon": 105.7333, "location": "Tu Liem, Ha Noi"},
            "detected_threats": [{"target": "person", "distance_m": distance, "bearing": "Tay"}],
        }
        process_payload(payload, gater)
        time.sleep(0.3)


def main():
    gater = TacticalAlertGater()

    # Warmup: goi 1 lan de tai mo hinh len GPU (lan dau co the 10-30s),
    # cac lan goi sau moi < 0.2s
    try:
        call_ollama("Tra ve dung 1 tu: An toan", timeout=90)
        print(f"[INFO] Mo hinh {MODEL} da nong (GPU). San sang nhan JSON.", flush=True)
    except Exception as exc:
        print(f"[LOI] Ollama chua chay hoac model chua co tai {OLLAMA_URL}: {exc}", file=sys.stderr)
        sys.exit(1)

    if "--demo" in sys.argv:
        run_demo(gater)
        return

    if not sys.stdin.isatty():
        print("[INFO] Do JSON tu stdin (moi dong/1 payload).", flush=True)
        for payload in iter_json_objects(sys.stdin.read()):
            process_payload(payload, gater)
    else:
        print("[INFO] Chua co JSON. Chay `python tactical_slm.py --demo` hoac pipe JSON tu stdin.", flush=True)


if __name__ == "__main__":
    main()
