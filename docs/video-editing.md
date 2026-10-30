# Video editing notes (open source only)

The 60-second cut is edited with open-source tools only. No Premiere/After Effects/CapCut.

## Stack

| Tool | Licence | Use here |
|---|---|---|
| **FFmpeg** | LGPL/GPL | capture mux, trims, punch-ins, overlays, captions, loudness, concat |
| **ImageMagick** | ImageMagick licence | labels, crops, storyboard, thumbnails |
| **Chromium DevTools Protocol** | BSD-style | records the real app at 1920×1080 and dispatches real mouse events |
| **Swar** (Naamche Labs) | MIT code / CC BY-SA weights | human-sounding synthetic voice; Maya preset |
| **ffprobe / pdfinfo** | part of FFmpeg / poppler | verification of duration, resolution, page counts |

No GUI editor is required. The whole cut is reproducible from `tools/record_demo.mjs`,
`tools/video_edit.py`, the source pages in `docs/assets/record/`, and the voice clips.

## Editing grammar used

1. **App-first** — open on the real UI, not a title card. Hook and quote are overlays over the
   app; they do not replace it.
2. **Punch-in, not fake zoom** — the R6 and R1 beats are crops of the *same recorded frames*,
   scaled to 1080p. This is standard factual-demo editing: show the receipt at a readable size.
3. **J-cut** — the voice line about the mandate starts before the cut into the right rail, so the
   viewer hears the claim before seeing the proof.
4. **Jump cut over model latency** — a real model call takes seconds; the cut skips the wait
   instead of speeding up the UI. The receipt that appears is the real one.
5. **Matched labels** — a small poster lower-third carries the exact rule
   (`BLOCKED · R0-instruction-from-data`) at 1080p.
6. **Evidence, not adjectives** — the frontier section is a raw JSON/report page, not a marketing
   card. It shows the command, the arms, 50% → 0%, and 18/18 receipts.
7. **Sound** — Swar voice, small room tone, gentle compression and loudness normalisation
   (`-16 LUFS`, `-1.5 dBTP`); no music bed to fight the words.
8. **Captions** — SRT generated from the same script, burned at small size; a clean version is
   shipped for anyone who wants the raw screen capture.

## Open-source editing references

- FFmpeg filters used: `crop`, `scale`, `zoompan`, `overlay`, `subtitles`, `tpad`, `concat`,
  `amix`, `adelay`, `loudnorm`, `acompressor`, `highpass`/`lowpass`.
- ImageMagick: `-crop`, `-resize`, `-extent`, `montage` for labels/storyboards.
- Caption timing is derived from the voice starts and checked with `ffprobe`/ASR.
- The screen recorder is a small CDP client; it uses Node's built-in `WebSocket`, no browser
  automation package.

## Reproduce

```bash
# app (real key in .env) and static pages
PYTHONPATH=src python3 -m onlyyou.cli web --port 8022
python3 -m http.server 8090 --directory docs/assets/record
python3 -m http.server 8091 --directory docs

# CDP browser
chromium --headless=new --remote-debugging-port=9333 --window-size=1920,1080 about:blank

# record
OUT=/tmp/rec-frames node tools/record_demo.mjs

# edit helpers (punch-in, overlay, captions, mux)
python3 tools/video_edit.py --help
```

The current final is `docs/demo-60s.mp4`; the uncaptioned screen recording is
`docs/demo-60s-clean.mp4`.
