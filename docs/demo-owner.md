# The owner-voice submission cut

**File:** `docs/demo-owner.mp4` · **2:16** · 1920×1080 · 30 fps · H.264/AAC · no burned captions.

This is the cut for the submission form: **under 3:00**, narrated in the owner's own
voice, cut to the voice rather than stretching the voice to an old timeline.

## What changed

- The owner's raw `m4a` was separated from background music/room noise (Demucs), then
  spectrally denoised (noisereduce), EQ'd, compressed, de-essed and normalized to −16 LUFS.
- The picture was rebuilt around the actual read: 17 beats, each one on the spoken line,
  not a 3-minute template with the voice squeezed into it.
- No captions were burned. The only text on screen is the product UI and small feature
  labels; the transcript lives in `docs/voice-script-3min.md` and the SRT can be regenerated.
- The real ledger is shown: six receipts, including one **R6-mandate allow** (electrician,
  $4,500), one **R1-payee-not-contact** block (attacker), and four **R0-instruction-from-data**
  blocks (stranger voice, poster, TV ad, hidden page text).
- The builder's real photo/credit appears on the open and close, so it reads as a person, not an
  anonymous screen recording.
- The merchant terminal resolves to **MERCHANT VERIFIED · PAID** with the QR receipt, then the
  receipt verification page; the frontier report, label layer, forged sensor results and roadmap
  are all on screen.

## Beat sheet

| Time | Voice / picture |
|---|---|
| 0:00 | Hook — “Your glasses can hear the world. The question is who they obey.” |
| 0:09 | Meta’s “not an enforced security boundary” quote |
| 0:15 | The ledger: stranger voice treated as data, R0 |
| 0:26 | Scene text is data, not command |
| 0:33 | Scoped mandate: payee, cap, expiry |
| 0:40 | Merchant terminal verifies the mandate offline, then **MERCHANT VERIFIED · PAID** |
| 0:47 | R6 receipt — electrician paid, allowed |
| 0:53 | R1 receipt — attacker payee blocked |
| 0:58 | Poster, TV ad, hidden page text — R0 |
| 1:05 | Every action and refusal on the record |
| 1:14 | Signed, hash-chained receipts |
| 1:22 | DeepSeek frontier run: 50% → 0%, 18/18 |
| 1:32 | Label layer: 81% recall, 14.3% false positives |
| 1:44 | Forged sensors: 6/6 → 0/6; adaptive 20% |
| 1:54 | What ten engineers would build next |
| 2:13 | Close — hand it your wallet |

## Honest notes

- The voice is the owner’s recording, cleaned — not cloned, not TTS.
- The screen recording is of the live app; the receipts are real and the ledger shown is
  the actual run. The owner’s take was 2:16, so the video is 2:16, not padded to 3:00.
- The microphone was a phone/room recording, so some denoising is audible. The cleaned
  master is `data/voice/owner-take-clean.wav` (gitignored). The raw take is not committed.
- `docs/demo-3min.mp4` is the older synthetic cut and is kept only as a fallback. The
  submission should use `docs/demo-owner.mp4`.
