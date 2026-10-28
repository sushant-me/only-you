# The 60-second cut

Two deliverables, same beats:

- **16:9** `docs/demo-60s.mp4` — 1920×1080, 60.000 s, captions `docs/demo-60s.srt`
- **9:16** `docs/demo-60s-vertical.mp4` — 1080×1920, 60.000 s, captions `docs/demo-60s-vertical.srt`

Both use **real UI states captured from a live server with `muse-spark-1.3`** (the badge is visible in the
UI and as an overlaid chip). The cursor, zooms, cards and captions are edited motion graphics, not a literal
screen recording; the receipts and verdicts are genuine.

## Beat sheet

| Time | Beat | Source |
|---|---|---|
| 0:00–0:03 | Hook | card |
| 0:03–0:07 | WebMCP quote | card |
| 0:07–0:13 | grant: empty UI → click → mandate | `state-pre`, `state-mandate` |
| 0:13–0:20 | owner pays; **allow · R6-mandate** | `state-paid` |
| 0:20–0:30 | attacker; **deny · R1-payee-not-contact** | `state-final` |
| 0:30–0:36 | poster; **BLOCKED · R0-instruction-from-data** | `poster-verdict` |
| 0:36–0:40 | frontier **50%** paid | card |
| 0:40–0:45 | gate **0%** · 18/18 receipts | card |
| 0:45–0:52 | browser **VERIFIED · CROSS-MODEL** | live verifier |
| 0:52–0:56 | close | card |
| 0:56–1:00 | links / CTA | card |

Cards are never held longer than 5 s; the attack/poster/verify beats carry continuous cursor + zoom motion.

## Recreate the UI states

With the server running (`make web`, real key in `.env`):

```bash
curl -s -X POST localhost:8000/api/reset -d '{}'
# screenshot -> empty state
curl -s -X POST localhost:8000/api/mandate \
  -H 'Content-Type: application/json' \
  -d '{"payees":["electrician"],"max_amount":5000,"ttl_seconds":86400}'
# screenshot -> mandate state
curl -s -X POST localhost:8000/api/command -H 'Content-Type: application/json' \
  -d '{"speaker":"owner","channel":"voice","text":"pay the electrician 4500","confirms":true}'
# screenshot -> R6 allow
curl -s -X POST localhost:8000/api/command -H 'Content-Type: application/json' \
  -d '{"speaker":"owner","channel":"voice","text":"pay @attacker0 5000","confirms":true}'
# screenshot -> R1 deny
```

The first 16:9 frame uses the `R1-payee-not-contact` receipt and the R6 allow, so the attack beat is not
spoiled before it happens.

## Edit the cut

- **Narration:** per-beat MP3s are the current audio bed; `docs/demo-60s.srt` is the full transcript.
- **Length:** the six card beats and five UI beats are independent clips; swap a card, keep the timestamps.
- **Style:** white on `#0b0e15`, red `#ff2d55` for deny/risk, green `#2fd18c` for allow/verified.
- Rebuild the 3-minute film separately (`docs/narration-script.md`); this cut is intentionally synthetic-
  narration and is labelled as such in `docs/limitations.md`.
