#!/usr/bin/env python3
"""SAM 3.1 grounding check: ask for an object phrase, record boxes, draw them.

    PYTHONPATH=src python3 tools/sam_check.py
    python3 tools/sam_check.py --image src/onlyyou/web/fakecam-invoice.jpg --prompt paper
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

from onlyyou.env import load_env
from onlyyou.sam import SamError, segment

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results-sam"


def annotate(source: Path, boxes: list[dict], target: Path) -> bool:
    draw = []
    for box in boxes:
        draw += ["-draw", f"rectangle {box['x1']},{box['y1']} {box['x2']},{box['y2']}"]
    command = [
        "magick", str(source), "-stroke", "#2fd18c", "-strokewidth", "4", "-fill", "none",
        *draw, str(target),
    ]
    try:
        subprocess.run(command, check=True, capture_output=True)
        return True
    except Exception:  # noqa: BLE001 - annotation is optional
        return False


def main() -> int:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--image",
        type=Path,
        action="append",
        default=None,
        help="image to segment (repeatable; default: demo invoice + a UI frame)",
    )
    parser.add_argument("--prompt", default="paper", help="short noun phrase")
    args = parser.parse_args()
    images = args.image or [
        ROOT / "src" / "onlyyou" / "web" / "fakecam-invoice.jpg",
        ROOT / "docs" / "img" / "youtube-thumb.jpg",
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": "sam-3.1",
        "prompt": args.prompt,
        "note": (
            "SAM returns object boxes over /v1/responses as special-token text; masks are not "
            "decoded here. Boxes are scene grounding (data), never authority."
        ),
        "runs": [],
    }
    for image in images:
        rel = str(image.relative_to(ROOT)) if image.is_relative_to(ROOT) else str(image)
        try:
            result = segment(image.read_bytes(), prompt=args.prompt)
        except SamError as exc:
            print(f"FAIL {rel}: {exc}")
            report["runs"].append({"image": rel, "error": str(exc)})
            continue
        out_png = OUT / (image.stem + "-sam.png")
        annotate(image, result["boxes"], out_png)
        run = {
            "image": rel,
            "boxes": result["boxes"],
            "regions": len(result["boxes"]),
            "raw_length": result["raw_length"],
            "annotated": str(out_png.relative_to(ROOT)) if out_png.exists() else None,
        }
        report["runs"].append(run)
        print(f"{rel}: {run['regions']} region(s) {run['boxes']}")

    (OUT / "sam.json").write_text(json.dumps(report, indent=2) + "\n")
    if len(report["runs"]) == 1:
        print("wrote results-sam/sam.json")
    return 0 if any("boxes" in run for run in report["runs"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
