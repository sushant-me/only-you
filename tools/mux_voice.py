#!/usr/bin/env python3
"""Mux a narration track onto the 2:59 captioned cut, loudness-normalised.

Two-pass loudnorm: measure the voice, then apply the measured values so the
speech lands at -16 LUFS while the video stream is copied untouched.
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

VIDEO = pathlib.Path("docs/demo-3min.mp4")
OUT = pathlib.Path("docs/demo-3min-voice.mp4")
DURATION = 179.0
TARGET = "I=-16:TP=-1.5:LRA=11"


def measure(voice: str) -> dict:
    cmd = [
        "ffmpeg", "-hide_banner", "-i", voice,
        "-af", f"loudnorm={TARGET}:print_format=json",
        "-f", "null", "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    blocks = re.findall(r"\{[^{}]+\}", proc.stderr)
    for block in reversed(blocks):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        if "input_i" in data:
            return data
    raise SystemExit("could not measure the voice track")


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: mux_voice.py narration.(wav|mp3|m4a)", file=sys.stderr)
        return 2
    voice = sys.argv[1]
    if not VIDEO.exists():
        raise SystemExit(f"missing {VIDEO}")
    stats = measure(voice)
    loud = (
        f"loudnorm={TARGET}"
        f":measured_I={stats['input_i']}:measured_TP={stats['input_tp']}"
        f":measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}"
        f":offset={stats['target_offset']}:linear=true"
    )
    chain = f"[1:a]aresample=48000,{loud},apad,atrim=0:{DURATION}[a]"
    cmd = [
        "ffmpeg", "-y", "-i", str(VIDEO), "-i", voice,
        "-filter_complex", chain,
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart", str(OUT),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stderr[-800:], file=sys.stderr)
        return 1
    print(f"wrote {OUT} ({DURATION:.0f}s, voice normalised to -16 LUFS)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
