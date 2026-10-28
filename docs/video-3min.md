# 3-minute demo video — shot list, script, and production notes

> **Current build:** `docs/demo-3min.mp4` — 175 s, silent, burned-in captions, frames from the current UI
> (Muse Image scene assets). It is the fallback if the live voice-over take is not ready. Rebuild recipe:
> capture the UI at 1600×900, add title/quote/benchmark/end cards, 11 segments with gentle push-in and a
> caption bar, concat. The script below is for the spoken take.

Deadline: **Nov 4, 9:00 PM ET** (Nov 5, 7:45 AM NPT). The video is scored directly; the repo and the
video are what judges see. Record at **1920×1080, 30 fps**, H.264 MP4, under 300 MB.

## Pre-flight (30 minutes)

- [ ] Demo server running: `make web` → http://127.0.0.1:8000
- [ ] `?fakecam=1&script=full` rehearsed once end-to-end; note the exact timings
- [ ] Mic tested (`arecord -d 3 /tmp/t.wav && aplay /tmp/t.wav`)
- [ ] Browser at 1600×900, zoom 100%, notifications off, no personal tabs
- [ ] Terminal font ≥ 16 pt if shown
- [ ] Screen recorder: `wf-recorder -g "$(slurp)" -f demo.mp4` (Wayland) or OBS
- [ ] Second screen for the script so you are not reading on camera

## Script (≈430 words, ≈3:00 at 145 wpm)

| Time | VO | On screen |
|---|---|---|
| 0:00 | "Your glasses can hear the world. The question is who they obey." | Title card over the UI, slow push-in |
| 0:08 | "This is ONLY YOU — the layer that decides who a wearable agent answers to." | UI wide shot, RED badge |
| 0:15 | "Meta's own docs say the untrusted-content flag is 'not an enforced security boundary.' The agent can't tell an instruction from content, or you from a stranger." | Highlight the quote; cut to a poster, a TV ad, an invoice |
| 0:30 | "So a TV ad, a poster, a look-alike invoice — all of them reach the same context window as your voice." | Three attacks flash on screen |
| 0:42 | "ONLY YOU fixes the channel, not the model. Only your enrolled voice is a command. Everything else is data: read, summarized, never obeyed." | Voice enrollment meter; `scene text detected` mask |
| 0:55 | "You write a constitution — never pay strangers, ask me over five thousand." | Constitution list |
| 1:02 | "And you hand out mandates: signed, scoped, expiring. Pay the electrician up to five thousand, until tomorrow." | Grant-mandate card appears, `valid` |
| 1:07 | "A merchant can verify that mandate offline, with only the public key." | Click *verify at merchant* → MERCHANT VERIFIED |
| 1:12 | "Now the agent can act without interrupting you." | Click *owner pays invoice* |
| 1:18 | "Paid. Receipt cites the mandate — no prompt, no interruption." | DONE card + receipt hash |
| 1:25 | "Now the same spoken command, with a different invoice." | Click *attacker invoice* |
| 1:32 | "Refused — because the payee came from a document, not from you." | BLOCKED R1 card |
| 1:40 | "A poster in the scene." | Click *poster tries to unlock* |
| 1:46 | "Scene text is masked as data. Read, never obeyed." | Mask + BLOCKED R0 |
| 1:53 | "A TV ad." | Click *TV ad tries to pay* |
| 1:58 | "Not your voice, not a command." | BLOCKED R0 |
| 2:03 | "Hidden page text." | Click *hidden page text* |
| 2:08 | "Same result." | BLOCKED R0 |
| 2:12 | "Then ask it what it did today." | Click *what did you do today?* |
| 2:18 | "Every action and every refusal is on the record: rule, evidence, source, hash chain." | Ledger answer, receipts rail |
| 2:28 | "We measured the part that can be wrong. Hidden-text labels: 81% recall, 14% false positives. Forged sensor signals: six of six executed without a signed sensor bus, zero with it." | Benchmark table, label layer + envelope |
| 2:40 | "And when the owner is present and confirms, the adaptive attacker still gets through 20% of the time. We publish that too." | Adaptive row + limitation line |
| 2:50 | "With ten engineers: tool-result provenance in WebMCP, voice and DOM provenance in the Muse client, and device-key mandates merchants can verify." | 3-item roadmap card |
| 3:00 | "Superintelligence is useless if it isn't yours. Repo and benchmark in the description." | End card |

## Shot list and edit

1. **Open** — title card 3 s, then UI. Add a red `REC` style badge? No, keep clean.
2. **Demo** — one continuous take of the script; if a beat fails, cut and re-enter at the last beat
   (do not fake the outcome).
3. **Insert shots** — quote card, poster/TV/invoice art (already in `src/onlyyou/web/fakecam-*.png`),
   benchmark table screenshot.
4. **Callouts** — circle the `R1-payee-not-contact` rule and the receipt hash; 1 s each.
5. **Captions** — burn in the hook, the quote, and the verdicts (BLOCKED / DONE). Muted viewers matter.
6. **Music** — optional, −22 dB under VO; no lyrics.

## Export and publish

```bash
ffmpeg -i demo-raw.mkv -vf "scale=1920:1080,fps=30" \
  -c:v libx264 -crf 20 -preset medium -c:a aac -b:a 160k -movflags +faststart demo.mp4
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 demo.mp4
```

Upload unlisted to YouTube, title **"ONLY YOU — the layer that decides who your agent obeys"**,
description: one-liner, repo link, benchmark link, and the honest caveat. Paste the link into the
submission form. Keep the original file for the finals.

## 45-second X cut (for the $20K viral prize)

Hook (0–5 s): the quote + "so I built the fix during their hackathon".
Beat (5–25 s): mandate → pay → look-alike invoice refused (the money shot).
Close (25–40 s): signed sensor 6/6 → 0/6, repo link.
Post **Nov 6–8**, reply to the hackathon post, pin it. Likes/reposts/comments by **Nov 8, 11:59 PM ET**.
