"""Repo self-audit for the submission.

Checks the claims a judge or a logged-out visitor would check: tests, benchmark
numbers in the docs, relative links, secrets, required artifacts, PDF page
counts, video durations. Exit 0 = submission-ready.

    PYTHONPATH=src python3 tools/audit.py
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
passed: list[str] = []
failed: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    (passed if ok else failed).append(f"{name}{(' — ' + detail) if detail else ''}")


def main() -> int:
    # tests
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=ROOT,
        env={**__import__("os").environ, "PYTHONPATH": "src", "ONLYYOU_MODEL": "simulated", "ONLYYOU_SKIP_BROWSER": "1"},
        capture_output=True,
        text=True,
    )
    check("test suite passes", proc.returncode == 0, "suite green" if proc.returncode == 0 else "failed")

    # benchmark numbers
    bench = ROOT / "results" / "benchmark.json"
    if bench.exists():
        b = json.loads(bench.read_text())
        arms = {m["arm"]: m for m in b["arms"]}
        check("benchmark mode is simulated", b.get("mode") == "simulated", str(b.get("mode")))
        check("arm A 100%", arms["A"]["attack_success_rate"] == 1.0)
        check("arm B 47.5%", arms["B"]["attack_success_rate"] == 0.475)
        check("arm C 10%", arms["C"]["attack_success_rate"] == 0.1)
        check("arm D 0%", arms["D"]["attack_success_rate"] == 0.0)
        check("DOM recall 81.0%", b["label_layer"]["dom"]["recall"] == 0.8095)
        check("DOM FPR 14.3%", b["label_layer"]["dom"]["false_positive_rate"] == 0.1429)
        check("adaptive 80/80/20", (b["adaptive"]["label_error_rate"], b["adaptive"]["proposal_rate"], b["adaptive"]["execution_rate"]) == (0.8, 0.8, 0.2))
        check("forged 6/6 -> 0/6", b["forged"]["plain_executed"] == 6 and b["forged"]["signed_executed"] == 0)
        check("scene detection 100% (35/35)", b["scene"]["detection_rate"] == 1.0)
    else:
        check("results/benchmark.json exists", False)

    # real-model runs (committed)
    for rel in ("results-real/benchmark.json", "results-real-doc/benchmark.json", "results-real-doc-contributor/benchmark.json"):
        path = ROOT / rel
        check(f"{rel} exists", path.exists())
        if path.exists():
            r = json.loads(path.read_text())
            check(f"{rel} mode meta", r.get("mode") == "meta", str(r.get("mode")))
            check(f"{rel} model muse-spark", "muse-spark" in str(r.get("model", "")))
    muse_scene = ROOT / "results/scene-muse.json"
    check("results/scene-muse.json exists", muse_scene.exists())
    if muse_scene.exists():
        m = json.loads(muse_scene.read_text())
        check("Muse Wonder scene sample 100%", m.get("detection_rate") == 1.0)
        check("Muse Wonder scene sample CER 0", m.get("mean_cer") == 0.0)

    for rel in ("results-real-doc/benchmark.json", "results-real-doc-contributor/benchmark.json"):
        doc_run = ROOT / rel
        if doc_run.exists():
            arms = {m["arm"]: m for m in json.loads(doc_run.read_text())["arms"]}
            check(f"{rel}: undefended > 0%", arms["A"]["attack_success_rate"] > 0)
            check(f"{rel}: full gate 0%", arms["D"]["attack_success_rate"] == 0.0)
            check(f"{rel}: full gate 0% false refusals", arms["D"]["false_refusal_rate"] == 0.0)

    # docs mention the key numbers
    text = "\n".join(
        p.read_text(errors="ignore") for p in ROOT.rglob("*.md") if p.name != "AUDIT.md"
    )
    for needle in ["171 tests", "81.0%", "14.3%", "100.0%", "1.7%", "6/6", "0/6", "Muse Spark", "Muse Wonder", "conditional"]:
        check(f"docs mention {needle}", needle in text)

    # no stale overclaims
    for bad in ["71 ms", "under 100 ms", "40/40", "0 false refusals", "100% secure"]:
        check(f"no stale claim {bad!r}", bad not in text)

    # secrets: a real key assignment in a tracked file
    secret_hits = []
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts or p.name in {".env.example", "AUDIT.md"}:
            continue
        if p.suffix not in {".py", ".md", ".js", ".html", ".json", ".yml", ".yaml", ".sh", ".txt"}:
            continue
        for line in p.read_text(errors="ignore").splitlines():
            if re.search(r"(META_API_KEY|META_API_BASE|OPEN_WEIGHTS_KEY)\s*=\s*\S+", line):
                secret_hits.append(f"{p.relative_to(ROOT)}: {line.strip()[:80]}")
    check("no secrets committed", not secret_hits, "; ".join(secret_hits[:3]))
    tracked_env = subprocess.run(
        ["git", "ls-files", ".env"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()
    ignored_env = subprocess.run(
        ["git", "check-ignore", "-q", ".env"], cwd=ROOT
    ).returncode == 0
    check(".env exists but is gitignored and untracked", not tracked_env and ignored_env)

    # relative links
    missing = []
    for p in (q for q in ROOT.rglob("*.md") if q.name != "AUDIT.md"):
        for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", p.read_text(errors="ignore")):
            target = m.group(2).split("#")[0]
            if not target or target.startswith(("http://", "https://", "mailto:", "image:")):
                continue
            if not (p.parent / target).resolve().exists():
                missing.append(f"{p.relative_to(ROOT)} -> {target}")
    check("relative links resolve", not missing, "; ".join(missing[:3]))

    # artifacts
    artifacts = {
        "docs/report.pdf": 2,
        "docs/pitch.pdf": 9,
        "docs/demo-task-clip.mp4": None,
        "docs/demo-fallback.mp4": None,
        "docs/demo-x-vertical.mp4": None,
        "docs/demo-3min.mp4": None,
        "docs/video-3min.md": None,
        "docs/live-finals.md": None,
        "docs/limitations.md": None,
        "BUILD_LOG.md": None,
        "README.md": None,
        "LICENSE": None,
    }
    for rel, pages in artifacts.items():
        path = ROOT / rel
        check(f"artifact {rel}", path.exists())
        if pages and path.exists():
            info = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True).stdout
            m = re.search(r"Pages:\s+(\d+)", info)
            check(f"{rel} has {pages} pages", bool(m) and int(m.group(1)) == pages, m.group(1) if m else "?")

    for extra in ("docs/demo-3min.srt", "docs/img/youtube-thumb.jpg"):
        check(f"artifact {extra}", (ROOT / extra).exists())

    for rel, expected in (("docs/demo-task-clip.mp4", 20.0), ("docs/demo-fallback.mp4", 82.0), ("docs/demo-3min.mp4", 175.0)):
        path = ROOT / rel
        if path.exists():
            info = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                capture_output=True,
                text=True,
            ).stdout.strip()
            check(f"{rel} duration {expected:.0f}s", abs(float(info) - expected) < 0.3, info)

    # git cleanliness (advisory)
    status = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout
    if os.environ.get("AUDIT_SKIP_GIT_CLEAN") == "1":
        check("git tree clean (skipped: working tree allowed for make judge)", True)
    else:
        check("git tree clean", status.strip() == "", status.strip()[:80])

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"# Repo audit — {now}\n")
    print(f"**{len(passed)} passed · {len(failed)} failed**\n")
    if failed:
        print("## Failures\n")
        for f in failed:
            print(f"- ❌ {f}")
        print()
    print("## Checks\n")
    for p in passed:
        print(f"- ✅ {p}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
