# Demo reel — silent, 29.6 s, 1600×900

`docs/demo-reel-captioned.mp4` is the version to share (captions burned in, so it works muted).
`docs/demo-reel.mp4` is the clean master.

It is a **silent screen reel** for the submission page, social posts, and B-roll.
It is not the 90-second pitch video: it has no voice-over and no face camera. Add the VO from
`video-script.md` on top, or use it as a fallback if you cannot screen-record.

## What it shows

| Time | Shot |
|---|---|
| 0–4 s | title card: ONLY YOU, the one-liner, the closing line |
| 4–8 s | invoice held to the wearer view; **DONE — R6-mandate**, receipt |
| 8–12 s | look-alike invoice; **BLOCKED — R1-payee-not-contact** |
| 12–16 s | poster; SAM mask + **BLOCKED — scene text** |
| 16–20 s | TV ad; **BLOCKED — a voice that isn't yours** |
| 20–24 s | hidden page text; **BLOCKED — hidden page content** |
| 24–28 s | ledger answer: actions, refusals, sources, chain intact |
| 28–30 s | results card + closing card |

The wearer view uses the `?fakecam=1` mode (static scene images in `src/onlyyou/web/fakecam-*.png`)
so the reel is reproducible on a headless machine with no camera.

## Rebuild

Requires: Chromium, FFmpeg, ImageMagick, and the demo server.

```bash
# 1. server
PYTHONPATH=src python3 -m onlyyou.cli web --port 8000 &

# 2. six UI frames (virtual time, deterministic)
for b in 2000 4600 6000 7400 8200 12000; do
  chromium --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
    --window-size=1600,900 --user-data-dir="/tmp/reel-$b" \
    --virtual-time-budget=$b --screenshot="/tmp/reel-t$b.png" \
    "http://127.0.0.1:8000/?script=full&fakecam=1"
done

# 3. three cards
for c in title results end; do
  chromium --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
    --window-size=1600,900 --user-data-dir="/tmp/card-$c" \
    --screenshot="/tmp/card-$c.png" "file://$PWD/docs/reel/$c.html"
done
```

Then assemble (four seconds per frame, 0.8 s crossfades):

```bash
ffmpeg -y \
  -loop 1 -t 4 -i /tmp/reel-title.png \
  -loop 1 -t 4 -i /tmp/reel-t2000.png \
  -loop 1 -t 4 -i /tmp/reel-t4600.png \
  -loop 1 -t 4 -i /tmp/reel-t6000.png \
  -loop 1 -t 4 -i /tmp/reel-t7400.png \
  -loop 1 -t 4 -i /tmp/reel-t8200.png \
  -loop 1 -t 4 -i /tmp/reel-t12000.png \
  -loop 1 -t 4 -i /tmp/card-results.png \
  -loop 1 -t 4 -i /tmp/card-end.png \
  -filter_complex "\
[0:v]scale=1600:900,settb=AVTB,fps=25,format=yuv420p[v0];\
[1:v]scale=1600:900,settb=AVTB,fps=25,format=yuv420p[v1];\
[2:v]scale=1600:900,settb=AVTB,fps=25,format=yuv420p[v2];\
[3:v]scale=1600:900,settb=AVTB,fps=25,format=yuv420p[v3];\
[4:v]scale=1600:900,settb=AVTB,fps=25,format=yuv420p[v4];\
[5:v]scale=1600:900,settb=AVTB,fps=25,format=yuv420p[v5];\
[6:v]scale=1600:900,settb=AVTB,fps=25,format=yuv420p[v6];\
[7:v]scale=1600:900,settb=AVTB,fps=25,format=yuv420p[v7];\
[8:v]scale=1600:900,settb=AVTB,fps=25,format=yuv420p[v8];\
[v0][v1]xfade=transition=fade:duration=0.8:offset=3.2[x1];\
[x1][v2]xfade=transition=fade:duration=0.8:offset=6.4[x2];\
[x2][v3]xfade=transition=fade:duration=0.8:offset=9.6[x3];\
[x3][v4]xfade=transition=fade:duration=0.8:offset=12.8[x4];\
[x4][v5]xfade=transition=fade:duration=0.8:offset=16.0[x5];\
[x5][v6]xfade=transition=fade:duration=0.8:offset=19.2[x6];\
[x6][v7]xfade=transition=fade:duration=0.8:offset=22.4[x7];\
[x7][v8]xfade=transition=fade:duration=0.8:offset=25.6[out]" \
  -map "[out]" -c:v libx264 -crf 20 -preset medium -movflags +faststart docs/demo-reel.mp4
```

## Captions

The captioned version is generated from the master with FFmpeg `drawtext`; the filter graph is in
`docs/reel/captions.filter`:

```bash
ffmpeg -y -i docs/demo-reel.mp4 -vf "$(cat docs/reel/captions.filter)" \
  -c:v libx264 -crf 20 -preset medium -movflags +faststart docs/demo-reel-captioned.mp4
```

## Notes

- The reel is **silent by design**; the pitch video needs your voice. Use the reel as B-roll or as the
  fallback if recording fails.
- Frames are captured at virtual times, so the UI state is deterministic; if a frame looks wrong,
  adjust the budget by ±400 ms and re-capture.
- Everything on screen is the real UI talking to the real demo server. No mocked screenshots.
