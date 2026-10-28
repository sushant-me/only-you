#!/usr/bin/env python3
"""Measure the local latency budget: routing, gate, OCR and the HTTP command path.

Deliberately excludes the network/model call: this is the part this repo can
claim. The report publishes exactly what is measured and what is not.
"""

from __future__ import annotations

import json
import platform
import statistics
import threading
import time
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from onlyyou.actions import Action
from onlyyou.ocr import ocr_png
from onlyyou.policy import Context
from onlyyou.webapp import DemoService, make_handler

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "latency.json"


def _stats(samples: list[float]) -> dict:
    samples = sorted(samples)
    pick = lambda q: samples[min(len(samples) - 1, int(q * len(samples)))]
    return {
        "n": len(samples),
        "p50_ms": round(statistics.median(samples), 3),
        "p95_ms": round(pick(0.95), 3),
        "mean_ms": round(statistics.fmean(samples), 3),
        "min_ms": round(samples[0], 3),
        "max_ms": round(samples[-1], 3),
    }


def bench(fn, n: int, warmup: int = 3) -> dict:
    for _ in range(warmup):
        fn()
    samples = []
    for _ in range(n):
        start = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - start) * 1000)
    return _stats(samples)


def main() -> int:
    service = DemoService()
    service.reset()
    service.grant_mandate({"payees": ["electrician"], "max_amount": 10 ** 9})
    invoice = {"payee": "electrician", "amount": 1}
    command = {
        "speaker": "owner",
        "channel": "document",
        "text": "pay this invoice",
        "payload": "INVOICE - ELECTRICIAN - 1",
        "invoice": invoice,
        "confirms": True,
    }
    image = (ROOT / "src" / "onlyyou" / "web" / "fakecam-invoice.jpg").read_bytes()

    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "model": "simulated (no network)",
        },
        "what_is_measured": [
            "constitution rules only (deterministic policy decision)",
            "dry-run path (routing + labels + constitution + mandates)",
            "full local command path (perception routing + simulated proposal + gate + receipt)",
            "scene OCR through tesseract on the demo invoice image",
            "HTTP POST /api/command against the real local server",
        ],
        "what_is_not_measured": [
            "model inference (Muse Spark / frontier), network and cold-start",
            "camera capture, browser rendering, speaker embedding (voice fixtures absent)",
        ],
        "constitution_only": bench(
            lambda: service.agent.constitution.evaluate(
                Action(kind="pay", params=invoice),
                Context(contacts={"electrician"}, pay_limit=1000, confirmed=True),
            ),
            n=1000,
            warmup=10,
        ),
        "dry_run_path": bench(
            lambda: service.simulate({"action": {"kind": "pay", "params": invoice}}), n=200
        ),
        "local_command": bench(lambda: service.command(dict(command)), n=50),
        "ocr": bench(lambda: ocr_png(image), n=7, warmup=1),
    }

    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(service))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"

    def http_command() -> None:
        body = json.dumps(command).encode()
        req = urllib.request.Request(
            base + "/api/command",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5):
            pass

    report["http_command"] = bench(http_command, n=30)
    report["constitution_only"]["note"] = "pure deterministic rules; no routing, no model"
    report["dry_run_path"]["note"] = "routing + labels + constitution + mandates; no model"
    report["local_command"]["note"] = "simulated proposal; excludes network/model inference"
    server.shutdown()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
