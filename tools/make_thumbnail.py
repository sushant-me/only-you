#!/usr/bin/env python3
"""Render docs/assets/youtube-thumb.html to docs/img/youtube-thumb.jpg."""
from __future__ import annotations
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "assets" / "youtube-thumb.html"
OUT = ROOT / "docs" / "img" / "youtube-thumb.jpg"


def main() -> int:
    tmp = Path("/tmp/onlyyou-thumb.png")
    subprocess.run(
        ["chromium", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
         "--window-size=1280,720", "--user-data-dir=/tmp/onlyyou-thumb-profile",
         "--virtual-time-budget=1500", f"--screenshot={tmp}", SRC.as_uri()],
        check=True, capture_output=True,
    )
    subprocess.run(["magick", str(tmp), "-quality", "88", str(OUT)], check=True)
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
