#!/usr/bin/env python3
"""Measure the Muse Wonder scene reader on a small synthetic sample.

Renders the same signs as the tesseract benchmark, reads them with Muse Wonder
(text + approximate boxes), and reports detection / character error rate. Small
n by design: this is the demo's perception path, not a field study.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from onlyyou.env import load_env  # noqa: E402
from onlyyou.scene_eval import PAYLOADS, cer, normalize, render, _keyword_hit  # noqa: E402
from onlyyou.scene_muse import muse_read  # noqa: E402

CONDITIONS = ["clean", "rotated", "low-contrast"]
OUT = pathlib.Path("results/scene-muse.json")


def main() -> int:
    load_env()
    rows = []
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        for payload in PAYLOADS:
            for cond in CONDITIONS:
                img = tmp / f"{abs(hash((payload, cond))) % 10**8}.png"
                if not render(payload, cond, img):
                    rows.append({"payload": payload, "condition": cond, "reader": None, "cer": 1.0, "detected": False})
                    continue
                result = muse_read(img.read_bytes())
                if result is None:
                    rows.append({"payload": payload, "condition": cond, "reader": None, "cer": 1.0, "detected": False})
                    continue
                text = result["text"]
                rows.append(
                    {
                        "payload": payload,
                        "condition": cond,
                        "reader": result["model"],
                        "boxes": len(result["lines"]),
                        "cer": round(cer(payload, text), 4),
                        "detected": _keyword_hit(payload, text),
                    }
                )
    n = len(rows)
    detected = sum(1 for r in rows if r["detected"])
    mean_cer = sum(r["cer"] for r in rows) / n if n else 0.0
    by_condition: dict[str, dict] = {}
    for r in rows:
        b = by_condition.setdefault(r["condition"], {"n": 0, "detected": 0, "cer_sum": 0.0})
        b["n"] += 1
        b["detected"] += int(r["detected"])
        b["cer_sum"] += r["cer"]
    for b in by_condition.values():
        b["cer"] = round(b.pop("cer_sum") / b["n"], 4)
        b["detection_rate"] = round(b["detected"] / b["n"], 4)
    report = {
        "model": "muse-wonder-1.0",
        "n": n,
        "conditions": CONDITIONS,
        "detection_rate": round(detected / n, 4) if n else 0.0,
        "mean_cer": round(mean_cer, 4),
        "by_condition": by_condition,
        "rows": rows,
        "note": (
            "Synthetic signs rendered with ImageMagick, read by Muse Wonder through the Meta Model API. "
            "Small n (5 payloads x 3 conditions); boxes are approximate. Not a field measurement."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))
    print(f"n={n} detection={report['detection_rate']*100:.1f}% mean_cer={report['mean_cer']*100:.1f}%")
    for cond, b in by_condition.items():
        print(f"  {cond:14s} {b['detection_rate']*100:5.1f}%  CER {b['cer']*100:5.1f}%")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
