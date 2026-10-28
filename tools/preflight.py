#!/usr/bin/env python3
"""Submission preflight: are the live links actually live, right now?

Run this immediately before pasting the submission. It checks the public repo,
the Pages site, every artifact a judge clicks, and the local submission files.
Exit code 0 only if all checks pass.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAGES = "https://sushant-me.github.io/only-you/"
URLS = [
    ("live page", PAGES),
    ("3-min video", PAGES + "demo-3min.mp4"),
    ("vertical video", PAGES + "demo-x-vertical.mp4"),
    ("fallback video", PAGES + "demo-fallback.mp4"),
    ("report PDF", PAGES + "report.pdf"),
    ("threat model", PAGES + "threat-model.md"),
    ("judge Q&A", PAGES + "judge-qa.md"),
    ("YouTube thumbnail", PAGES + "img/youtube-thumb.jpg"),
]
LOCAL = [
    "docs/submission-final.md",
    "docs/form-paste.txt",
    "docs/narration-script.md",
    "docs/demo-3min.mp4",
    "docs/demo-3min.srt",
    "docs/demo-3min.vtt",
    "docs/playground.html",
    "docs/verify.html",
    "docs/audit-sample.json",
    "NOTICE.md",
    "Dockerfile",
    "docker-compose.yml",
    "docs/deploy.md",
    "docs/img/invoice-scene.jpg",
    "docs/brief.pdf",
    "docs/frontier.md",
    "docs/voice-study.md",
    "docs/cross-model.md",
    "docs/cross-model-audit.json",
    "results-cross-model/cross-model-audit.json",
    "docs/press.md",
    "docs/img/x-stat.png",
    "docs/img/x-quote.png",
    "docs/brief.md",
    "docs/report.pdf",
    "docs/pitch.pdf",
    "docs/threat-model.md",
    "docs/judge-qa.md",
    "results/latency.json",
    "results-real/benchmark.json",
    "results-real-doc/benchmark.json",
    "results-real-doc-contributor/benchmark.json",
]


def head(url: str) -> tuple[bool, str]:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "only-you-preflight"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            size = len(resp.read(4096))
            return resp.status == 200 and size > 0, f"{resp.status}, first bytes {size}"
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return False, type(exc).__name__


def main() -> int:
    failures = 0
    print("LIVE LINKS")
    for name, url in URLS:
        ok, detail = head(url)
        failures += 0 if ok else 1
        print(f"  {'PASS' if ok else 'FAIL'}  {name:20s} {detail}")

    print("GITHUB")
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/sushant-me/only-you",
            headers={"User-Agent": "only-you-preflight", "Accept": "application/vnd.github+json"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
        public = data.get("private") is False and data.get("visibility") == "public"
        failures += 0 if public else 1
        print(f"  {'PASS' if public else 'FAIL'}  repo public          {data.get('html_url')}")
    except Exception as exc:  # noqa: BLE001
        failures += 1
        print(f"  FAIL  repo public          {type(exc).__name__}")

    tracked_env = subprocess.run(
        ["git", "ls-files", ".env"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()
    ok = not tracked_env
    failures += 0 if ok else 1
    print(f"  {'PASS' if ok else 'FAIL'}  .env not tracked     {'clean' if ok else tracked_env}")

    print("LOCAL FILES")
    for rel in LOCAL:
        path = ROOT / rel
        ok = path.exists() and path.stat().st_size > 0
        failures += 0 if ok else 1
        size = path.stat().st_size if path.exists() else 0
        print(f"  {'PASS' if ok else 'FAIL'}  {rel:34s} {size} bytes")

    print()
    if failures:
        print(f"{failures} check(s) failed — fix before submitting.")
    else:
        print("all checks passed — paste the form.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
