#!/usr/bin/env python3
"""Small, auditable open-source video-edit helpers (FFmpeg only).

These are the three operations the 60-second cut actually needs:
  punch-in     crop a real recorded frame region and scale it to 1080p
  overlay      put a transparent PNG over a video for a time window
  captions     burn an SRT with a readable style
  mux          attach a voice track and trim/pad to an exact duration

No GUI editor, no proprietary API. Run `python3 tools/video_edit.py <cmd> -h`.
"""

from __future__ import annotations

import argparse
import subprocess


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def punch_in(args: argparse.Namespace) -> None:
    """Crop x,y,w,h from source at start for dur seconds, scale to 1920x1080."""
    vf = f"crop={args.w}:{args.h}:{args.x}:{args.y},scale=1920:1080:flags=lanczos"
    if args.zoom:
        vf += ",zoompan=z='min(zoom+0.0007,1.07)':d=1:s=1920x1080:fps=30"
    run([
        "ffmpeg", "-v", "error", "-y", "-ss", str(args.start), "-t", str(args.duration),
        "-i", args.input, "-vf", vf, "-an", "-r", "30",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", args.output,
    ])


def overlay(args: argparse.Namespace) -> None:
    enable = f"between(t,{args.start},{args.end})"
    run([
        "ffmpeg", "-v", "error", "-y", "-i", args.input, "-i", args.png,
        "-filter_complex", f"[0:v][1:v]overlay={args.x}:{args.y}:enable='{enable}'[v]",
        "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-crf", "19", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-c:a", "copy", "-t", str(args.duration), args.output,
    ])


def captions(args: argparse.Namespace) -> None:
    style = (
        "FontName=Liberation Sans,FontSize=12,PrimaryColour=&Hffffff&,"
        "OutlineColour=&H000000&,BorderStyle=1,Outline=2,Shadow=0,MarginV=63"
    )
    run([
        "ffmpeg", "-v", "error", "-y", "-i", args.input,
        "-vf", f"subtitles={args.srt}:force_style='{style}'",
        "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-r", "30", "-c:a", "copy", "-t", str(args.duration), args.output,
    ])


def mux(args: argparse.Namespace) -> None:
    run([
        "ffmpeg", "-v", "error", "-y", "-i", args.video, "-i", args.audio,
        "-filter_complex", f"[1:a]apad,atrim=0:{args.duration},asetpts=PTS-STARTPTS[a]",
        "-map", "0:v", "-map", "[a]", "-t", str(args.duration),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", args.output,
    ])


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("punch-in", help="crop a frame region to 1080p")
    a.add_argument("input")
    a.add_argument("output")
    a.add_argument("start", type=float)
    a.add_argument("duration", type=float)
    a.add_argument("--x", type=int, required=True)
    a.add_argument("--y", type=int, required=True)
    a.add_argument("--w", type=int, required=True)
    a.add_argument("--h", type=int, required=True)
    a.add_argument("--zoom", action="store_true")
    a.set_defaults(func=punch_in)

    a = sub.add_parser("overlay", help="overlay a PNG for a time window")
    a.add_argument("input")
    a.add_argument("png")
    a.add_argument("output")
    a.add_argument("--start", type=float, required=True)
    a.add_argument("--end", type=float, required=True)
    a.add_argument("--duration", type=float, required=True)
    a.add_argument("--x", type=int, default=60)
    a.add_argument("--y", type=int, default=920)
    a.set_defaults(func=overlay)

    a = sub.add_parser("captions", help="burn an SRT")
    a.add_argument("input")
    a.add_argument("srt")
    a.add_argument("output")
    a.add_argument("--duration", type=float, default=60)
    a.set_defaults(func=captions)

    a = sub.add_parser("mux", help="attach voice and fix duration")
    a.add_argument("video")
    a.add_argument("audio")
    a.add_argument("output")
    a.add_argument("--duration", type=float, default=60)
    a.set_defaults(func=mux)

    args = p.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
