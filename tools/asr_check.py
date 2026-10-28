#!/usr/bin/env python3
"""Transcribe a WAV with Muse Voice Transcribe through the demo path.

    PYTHONPATH=src python3 tools/asr_check.py --wav data/voice-study/asr-sample.wav
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from onlyyou.env import load_env
from onlyyou.voice_muse import transcribe_wav

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--wav", type=Path, default=ROOT / "data" / "voice-study" / "asr-sample.wav")
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "voice-asr.json")
    args = parser.parse_args()
    result = transcribe_wav(args.wav.read_bytes())
    if result is None:
        print("transcription unavailable (no Meta key or endpoint error)")
        return 2
    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "wav": str(args.wav.relative_to(ROOT)),
        "model": result["model"],
        "transcript": result["text"],
        "note": "Muse Voice Transcribe over /v1/asr/transcribe; transcript is text and still passes the voice check + gate.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
