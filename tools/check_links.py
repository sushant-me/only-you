#!/usr/bin/env python3
"""Fail if a link in the static pages points at a file that is not in the repo.

Only local references are checked (http(s), mailto, anchors and data URIs are skipped),
which is exactly the class of breakage that ships silently when docs move.
"""

from __future__ import annotations

import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["docs/index.html", "docs/playground.html", "docs/verify.html"]


def main() -> int:
    failures: list[str] = []
    checked = 0
    for page in PAGES:
        html = (ROOT / page).read_text(encoding="utf-8")
        for attr in re.findall(r'(?:href|src)="([^"]+)"', html):
            if attr.startswith(("http://", "https://", "mailto:", "#", "data:")):
                continue
            parsed = urllib.parse.urlparse(attr)
            if parsed.scheme or parsed.netloc:
                continue
            target = (ROOT / page).parent / urllib.parse.unquote(parsed.path)
            checked += 1
            if not target.exists():
                failures.append(f"{page}: {attr} -> missing {target.relative_to(ROOT)}")
    if failures:
        print("dead local links:")
        for failure in failures:
            print("  FAIL", failure)
        return 1
    print(f"links ok: {checked} local references across {len(PAGES)} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
