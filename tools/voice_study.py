#!/usr/bin/env python3
"""Speaker-verification study harness: owner clips vs impostor clips.

Usage:
    python3 tools/voice_study.py --owner data/voice-study/owner --impostors data/voice-study/impostors

Any format ffmpeg can read is accepted; each clip is converted to 16 kHz mono WAV,
scored with the same MFCC voiceprint the demo uses, and reported as accepted/rejected.
Results are written to results/voice-study.json so a study is reproducible.

This measures the *channel check*, not anti-spoofing: a cloned voice with the same
timbre will pass. Human-subject numbers require real consented recordings.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from onlyyou.voice import enroll, verify

ROOT = Path(__file__).resolve().parents[1]
AUDIO_SUFFIXES = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".opus", ".webm"}


def load_audio(path: Path) -> bytes:
    if path.suffix.lower() == ".wav":
        return path.read_bytes()
    exe = shutil.which("ffmpeg")
    if exe is None:
        raise RuntimeError(f"ffmpeg is required to read {path.name}")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
        tmp = Path(handle.name)
    try:
        subprocess.run(
            [exe, "-v", "error", "-y", "-i", str(path), "-ac", "1", "-ar", "16000", str(tmp)],
            check=True,
        )
        return tmp.read_bytes()
    finally:
        tmp.unlink(missing_ok=True)


def clips(directory: Path) -> list[Path]:
    return sorted(
        p
        for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in AUDIO_SUFFIXES and p.stat().st_size > 1024
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", required=True, type=Path, help="directory of owner clips")
    parser.add_argument("--impostors", required=True, type=Path, help="directory of impostor clips")
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "voice-study.json")
    parser.add_argument("--threshold", type=float, default=None, help="override the learned threshold")
    args = parser.parse_args()

    owner_files = clips(args.owner)
    impostor_files = clips(args.impostors)
    if len(owner_files) < 1 or len(impostor_files) < 1:
        print("need at least one owner clip and one impostor clip")
        return 2

    def scored(files: list[Path], label: str) -> list[dict]:
        rows = []
        for path in files:
            try:
                rows.append({"clip": path.name, **verify(voiceprint, load_audio(path))})
            except Exception as exc:  # noqa: BLE001 — report bad clips, keep the study going
                print(f"  skip {label} {path.name}: {exc}")
        return rows

    try:
        voiceprint = enroll([load_audio(p) for p in owner_files])
    except Exception as exc:  # noqa: BLE001
        print(f"could not enroll from owner clips: {exc}")
        return 2
    if args.threshold is not None:
        voiceprint.threshold = args.threshold
    self_results = scored(owner_files, "owner")
    impostor_results = scored(impostor_files, "impostor")
    accepted_owner = sum(1 for r in self_results if r["accept"])
    accepted_impostors = sum(1 for r in impostor_results if r["accept"])
    report = {
        "owner_clips": len(owner_files),
        "impostor_clips": len(impostor_files),
        "threshold": voiceprint.threshold,
        "threshold_override": args.threshold is not None,
        "owner_accept_rate": round(accepted_owner / len(owner_files), 4),
        "impostor_false_accept_rate": round(accepted_impostors / len(impostor_files), 4),
        "owner_results": self_results,
        "impostor_results": impostor_results,
        "note": (
            "MFCC voiceprint threshold from the demo. Measures the channel check, not anti-spoofing; "
            "human-subject numbers require real consented recordings."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in (
        "owner_clips", "impostor_clips", "threshold", "owner_accept_rate",
        "impostor_false_accept_rate")}, indent=2))
    for row in self_results:
        print(f"  owner     {row['clip']:<32} distance={row['distance']:.3f} accept={row['accept']}")
    for row in impostor_results:
        print(f"  impostor  {row['clip']:<32} distance={row['distance']:.3f} accept={row['accept']}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
