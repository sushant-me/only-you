# YouTube upload — the 3-minute demo

File: [`demo-3min.mp4`](demo-3min.mp4) · 2:55 · 1600×900 · narrated (synthetic draft) + captioned · thumbnail: [`img/youtube-thumb.jpg`](img/youtube-thumb.jpg) · captions: [`demo-3min.srt`](demo-3min.srt)
Thumbnail: [`img/thumb.png`](img/thumb.png) (1280×720)

## Settings

| Field | Value |
|---|---|
| Visibility | **Unlisted** (check it plays in a logged-out browser) |
| Category | Science & Technology |
| Title | `ONLY YOU — the layer that decides who your agent obeys` |
| Language | English |
| Audience | Not made for kids |
| Comments | Off (or on — either is fine) |

## Description

```
The more capable the model, the more it needs an authority layer. Capability is solved. Authority isn't.

Your glasses can hear the world. Who do they obey?

Meta's own WebMCP docs say the untrusted-content flag is "not an enforced security
boundary" — and the assistant cannot tell the wearer's voice from a stranger's.
ONLY YOU fixes the channel: only the enrolled voice is a command, scene/page/document
text is data, irreversible actions need a signed mandate, and every action and every
refusal leaves a verifiable receipt.

Built during the Meta Global AI Developer Hackathon 2026. 172 tests, a four-arm benchmark,
and a published failure list — including the 20% of adaptive attacks that still get through.

Chapters (match the rebuilt 175 s captioned cut)
0:00 Who does your agent answer to
0:12 The gap
0:28 Meta's own warning
0:44 A mandate, then paid without a prompt
1:02 The look-alike invoice is refused
1:18 A poster is scene data
1:32 A TV ad is not your voice
1:46 Hidden page text
2:00 The record
2:16 Real-model numbers
2:36 Close

20-second contrast clip (undefended vs gated): https://github.com/sushant-me/only-you/blob/main/docs/demo-contrast.mp4
Play it yourself (no install): https://sushant-me.github.io/only-you/playground.html
Repo: https://github.com/sushant-me/only-you
Benchmark: https://github.com/sushant-me/only-you/blob/main/results/benchmark.md
Report: https://github.com/sushant-me/only-you/blob/main/docs/report.pdf
Run it: make judge  ·  docker run --rm -p 8000:8000 only-you-demo

Narration is a neural-TTS draft over the captioned cut; captions included (SRT in the repo).
```

## Tags

`AI agents, wearable AI, Meta, Muse, WebMCP, prompt injection, provenance, agent security,
hackathon, trust, receipts, mandates`

## Replacing the narration (optional)

The uploaded cut already has an aligned neural-TTS narration draft. If you prefer your own voice:

- Record over the same timeline (the chapters above match the captions), then `make voice VOICE=...`.
- Re-export and upload as a new version; keep the same title.
- Update the submission link only after the new version plays logged out.

## Upload the SRT

YouTube → Subtitles → Add → Upload file → `docs/demo-3min.srt` (it matches the burned-in captions and the
chapters). Set the thumbnail to `docs/img/youtube-thumb.jpg` (1280×720).

## Checklist

- [ ] File is ≤ 3:00 (this one is 2:55)
- [ ] Plays logged out
- [ ] Thumbnail uploaded
- [ ] Description links filled in after the repo is public
- [ ] Link pasted into the CV submission form
