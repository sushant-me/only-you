#!/usr/bin/env python3
"""End-to-end spoken command: Muse Voice Transcribe -> voice check -> gate -> receipt.

    PYTHONPATH=src python3 tools/voice_e2e.py --wav data/voice-study/asr-sample.wav

The transcript is treated as text, exactly like a typed command: it must pass the
voice check and the constitution/mandate gate. The transcript is imperfect on
purpose — the point is that ASR errors cannot bypass authority.
"""

from __future__ import annotations

import base64
import json
import time
from pathlib import Path

from onlyyou.env import load_env
from onlyyou.voice_muse import transcribe_wav
from onlyyou.webapp import DemoService

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    load_env()
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--wav", type=Path, default=ROOT / "data" / "voice-study" / "asr-sample.wav")
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "voice-e2e.json")
    args = parser.parse_args()
    wav = args.wav.read_bytes()

    asr = transcribe_wav(wav)
    if asr is None:
        print("no ASR available (META_API_* missing or endpoint error)")
        return 2
    service = DemoService()
    service.reset()
    service.grant_mandate({"payees": ["electrician"], "max_amount": 5000})
    encoded = base64.b64encode(wav).decode()
    service.voice_enroll({"clips": [encoded]})
    verification = service.voice_verify({"clip": encoded}).get("verification", {})
    result = service.command(
        {
            "speaker": "owner",
            "channel": "voice",
            "text": asr["text"],
            "payload": asr["text"],
            "confirms": True,
        }
    )
    verdict = result.get("verdict") or {}
    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "wav": str(args.wav.relative_to(ROOT)),
        "asr": {"model": asr["model"], "transcript": asr["text"]},
        "voice_check": {
            "accept": verification.get("accept"),
            "distance": verification.get("distance"),
            "threshold": verification.get("threshold"),
        },
        "command": {
            "outcome": result.get("outcome"),
            "rule": verdict.get("rule"),
            "action": result.get("action"),
            "receipt": (result.get("receipt") or {}).get("signature", "")[:16] or None,
        },
        "note": (
            "ASR is imperfect (it repeats a word in the sample); the transcript is still only text and "
            "must pass the voice check and the gate. This is the real spoken-command path."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["command"]["outcome"] == "executed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
