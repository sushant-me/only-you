# The 60-second cut

**This is a screen recording of the live app, not a motion-graphics assembly.**

- **16:9** `docs/demo-60s.mp4` — 1920×1080, 60.000 s, captioned
- **16:9 clean** `docs/demo-60s-clean.mp4` — same cut, no burned captions
- **Captions** `docs/demo-60s.srt`

The capture is from the real demo server with a real Meta key; the badge reads
`model: muse-spark-1.3`. The run shows a real mandate, a real `R6-mandate` allow, a real
`R1-payee-not-contact` block, a real `R0-instruction-from-data` refusal and the live
`verify.html` page. Mouse movement and clicks are dispatched into the page and recorded
with it; the pointer is a page overlay because a headless capture does not include the
OS cursor. Cursor, clicks, page loads and verdicts are real interactions, not a
frame-by-frame animation.

**Voice:** Swar (Naamche Labs), Maya preset — a synthetic Nepali-accented English voice
chosen because it sounds like a person rather than a flat screen-reader. It is still a
synthetic voice (not a microphone recording of the owner), and it is disclosed here and
in `docs/limitations.md`. The voice was generated from the same 60-second script and
mixed with a small room tone; no voice cloning of a real person is used.

## Beat sheet

| Time | On screen | Evidence |
|---|---|---|
| 0:00–0:03 | hook page, cursor | — |
| 0:03–0:07 | WebMCP quote page | quote |
| 0:07–0:13 | live app; grant mandate | `R6-mandate` appears |
| 0:13–0:20 | owner pays | green allow receipt |
| 0:20–0:30 | attacker invoice | red `R1-payee-not-contact`; counters 1 blocked / 1 allowed / 2 receipts |
| 0:30–0:36 | poster scan | red scene mask + `R0-instruction-from-data` label |
| 0:36–0:45 | frontier page | DeepSeek 50% → 0%, 18/18 receipts |
| 0:45–0:52 | live browser verifier | `VERIFIED · CROSS-MODEL` |
| 0:52–1:00 | close / links | — |

The app page is 1920×1080 and is recorded at that size. The R6 and R1 beats are **punch-ins**:
crops of the same recorded right-rail frames, scaled to 1080p so the receipt and counters are
readable on a phone. The verifier beat gets the same treatment. The poster lower-third is a
small label added in post. These are ordinary factual-demo edits — the pixels are from the
live recording, not rebuilt graphics. Editing notes: `docs/video-editing.md`.

## Captions

`docs/demo-60s.srt` is the full transcript. The captioned file burns it in with a
small bottom subtitle; `docs/demo-60s-clean.mp4` is the same video without burned
captions for a more raw screen-recording feel.

## Recreate the states

The server is the normal demo (`make web` or `python -m onlyyou.cli web --port 8022`)
with the real Meta key in `.env`; the app is opened with `?fakecam=1`. The UI actions are
the normal demo buttons: `8 · grant a mandate`, `1 · owner pays invoice`,
`5 · attacker invoice`, `3 · poster tries to unlock`. The verifier is
`docs/verify.html?auto=cross` served from the repository.

The recording is driven by `tools/record_demo.mjs` (Chromium DevTools Protocol at
1920×1080); its frontier/close pages are in `docs/assets/record/`. It dispatches the same
clicks a person would. `tools/video_edit.py` contains the open-source FFmpeg helpers used for
the punch-ins, overlays and captions. The old motion-graphics cut is superseded.
