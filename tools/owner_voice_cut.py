#!/usr/bin/env python3
"""Fit the owner's one-take voice-over to the 60-second cut.

The owner records one continuous take. This tool trims only the head/tail,
normalizes, fits the take to 60.000 s with a small (inaudible) tempo change,
and muxes it with the picture. It never cuts the take into lines.

Usage:
  python3 tools/owner_voice_cut.py data/voice/owner-take.wav \
      --video docs/demo-60s-clean.mp4 --out /tmp/owner-cut.mp4

  # optional music bed, already ducked by this tool
  python3 tools/owner_voice_cut.py take.wav --video cut.mp4 --out out.mp4 \
      --bed music.wav

The tool refuses a take outside 56.5–63.5 s or one that needs more than a
4% tempo change: a bigger change is audible and would break the natural flow.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

DURATION = 60.0
LEAD = 0.35
TARGET = DURATION - LEAD - 0.15  # leave a little room at the tail
MIN_TAKE = 56.5
MAX_TAKE = 63.5
MAX_TEMPO_DELTA = 0.04


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True)


def probe_duration(path: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ])
    return float(out.strip())


def loudness(path: Path) -> dict[str, float]:
    """Return integrated LUFS / true peak from ffmpeg's ebur128 output."""
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True, check=True,
    ).stderr
    integrated = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    peaks = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", out)
    return {
        "lufs": float(integrated[-1]) if integrated else 0.0,
        "peak_db": float(peaks[-1]) if peaks else 0.0,
    }


def prepare_voice(src: Path, tmp: Path) -> tuple[Path, float, float]:
    """Trim edges, clean, normalize. Returns (path, original_s, fitted_s)."""
    cleaned = tmp / "voice-clean.wav"
    # Trim only leading/trailing silence; keep every pause inside the take.
    run([
        "ffmpeg", "-v", "error", "-y", "-i", src,
        "-af",
        "silenceremove=start_periods=1:start_duration=0:start_threshold=-45dB,"
        "areverse,silenceremove=start_periods=1:start_duration=0:start_threshold=-45dB,areverse,"
        "highpass=f=70,lowpass=f=14000,"
        "acompressor=threshold=-20dB:ratio=2:attack=10:release=180,"
        "loudnorm=I=-16:TP=-1.5:LRA=9",
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", cleaned,
    ])
    natural = probe_duration(cleaned)
    if not (MIN_TAKE <= natural <= MAX_TAKE):
        raise SystemExit(
            f"take is {natural:.2f}s after trimming; expected {MIN_TAKE:.1f}–{MAX_TAKE:.1f}s.\n"
            "A bigger stretch would be audible. Re-read to the teleprompter and keep one take."
        )
    tempo = natural / TARGET
    if abs(tempo - 1.0) > MAX_TEMPO_DELTA:
        raise SystemExit(
            f"take needs a {abs(tempo - 1) * 100:.1f}% tempo change ({natural:.2f}s → {TARGET:.2f}s).\n"
            "That is audible. Re-read at the target pace instead of stretching it."
        )
    fitted = tmp / "voice-fit.wav"
    run([
        "ffmpeg", "-v", "error", "-y", "-i", cleaned,
        "-af",
        f"atempo={tempo:.6f},adelay={int(LEAD * 1000)}|{int(LEAD * 1000)},"
        f"apad=whole_dur={DURATION},atrim=0:{DURATION},asetpts=N/SR/TB",
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", fitted,
    ])
    return fitted, natural, tempo


def make_bed(tmp: Path, path: Path | None, voice: Path) -> Path | None:
    """Optionally build a quiet music bed, ducked under the voice.

    A supplied `--bed` file is looped/trimmed. With no file, no music is added:
    a synthetic drone is worse than clean silence.
    """
    if path is None:
        return None
    bed = tmp / "bed.wav"
    run([
        "ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", path,
        "-af", f"atrim=0:{DURATION},volume=0.18,afade=t=in:st=0:d=1.2,"
               f"afade=t=out:st={DURATION - 1.2}:d=1.2",
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", bed,
    ])
    return bed


def duck_and_mix(voice: Path, bed: Path | None, out: Path) -> Path:
    if bed is None:
        out.write_bytes(voice.read_bytes())
        return out
    # Sidechain-duck the bed under the voice so words stay on top.
    run([
        "ffmpeg", "-v", "error", "-y", "-i", voice, "-i", bed,
        "-filter_complex",
        "[1:a][0:a]sidechaincompress=threshold=0.035:ratio=9:attack=15:release=380[duck];"
        "[0:a][duck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
        "-map", "[a]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", out,
    ])
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("voice")
    p.add_argument("--video", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--bed", help="optional music bed (already licensed)")
    p.add_argument("--report", help="write a JSON report here")
    args = p.parse_args()

    src = Path(args.voice)
    video = Path(args.video)
    out = Path(args.out)
    if not src.exists():
        raise SystemExit(f"no such voice file: {src}")
    if not video.exists():
        raise SystemExit(f"no such video: {video}")

    with tempfile.TemporaryDirectory(prefix="onlyyou-voice-") as td:
        tmp = Path(td)
        voice, natural, tempo = prepare_voice(src, tmp)
        bed = make_bed(tmp, Path(args.bed) if args.bed else None, voice)
        mixed = duck_and_mix(voice, bed, tmp / "voice-mixed.wav")

        run([
            "ffmpeg", "-v", "error", "-y", "-i", video, "-i", mixed,
            "-map", "0:v", "-map", "1:a", "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-t", str(DURATION),
            "-movflags", "+faststart", out,
        ])

        levels = loudness(mixed)
        report = {
            "voice": str(src),
            "video": str(video),
            "out": str(out),
            "natural_s": round(natural, 3),
            "tempo": round(tempo, 5),
            "status": "ok",
            **{k: round(v, 2) for k, v in levels.items()},
        }
        print(json.dumps(report, indent=2))
        if args.report:
            Path(args.report).write_text(json.dumps(report, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
