# Owner voice-over — 3-minute submission cut

**Submission requirement: ≤ 3:00.** Aim for **2:50–2:58**. Read it as one continuous
take; do not record it line by line. The existing cut is 2:59, so this script is timed
to the burned-in captions.

**≈430 words · ≈145 words per minute.** Do not rush; if you finish early, hold the
last beat. If you run long, do not speed up — send the take and I will fit it with a
small, inaudible tempo change.

Open the [3-minute teleprompter](voice-teleprompter-3min.html) while recording.

## Transcript

**0:04**
Your glasses can hear the world. The question is who they obey. This is ONLY YOU — the layer that decides who a wearable agent answers to.

**0:16**
Meta's own docs say the untrusted-content flag is not an enforced security boundary. The agent can't tell an instruction from content, or you from a stranger.

**0:32**
So a TV ad, a poster, a look-alike invoice — all reach the same context window as your voice. I fixed the channel, not the model.

**0:48**
Only your enrolled voice is a command. Everything else is data: read, summarised, never obeyed. You write a constitution, and hand out signed, scoped, expiring mandates.

**1:06**
Pay the electrician up to five thousand until tomorrow. A merchant can verify that mandate offline with only the public key. Then the agent can act without interrupting you.

**1:22**
Paid. The receipt cites the mandate. Now the same spoken command, with a different invoice — refused, because the payee came from a document, not from you.

**1:36**
A poster in the scene: masked as data, read, never obeyed. A TV ad: not your voice, not a command.

**1:50**
Hidden page text: same result. Then ask it what it did today. Every action and every refusal is on the record: rule, evidence, source, hash chain.

**2:04**
We measured the part that can be wrong. Muse Spark executed twenty-five percent of confused-deputy attacks undefended, fifty percent with provenance only — and zero with the full gate, zero false refusals.

**2:20**
Label layer: eighty-one percent recall, fourteen percent false positives. Forged sensor signals: six of six without a signed sensor bus, zero with it. Adaptive corpus: twenty percent still get through. We publish that too.

**2:40**
With ten engineers: tool-result provenance in WebMCP, SAM masks and voice provenance in the Muse client, device-key mandates merchants can verify. Superintelligence is useless if it isn't yours. Repo and benchmark in the description.

## Delivery

- **One continuous read, 2:50–2:58.** The timestamps are beats, not stops.
- First person: “I fixed the channel,” “I measured.” You are the builder, not a narrator.
- Say the numbers plainly: **twenty-five, fifty, zero, eighty-one, fourteen, six, zero, twenty**. They are the evidence.
- Slight emphasis on **“not an enforced security boundary.”** It is a quote.
- One beat of silence before **“refused”** and before **“zero with the full gate.”**
- Last line: slower, drop your pitch on **“yours.”**
- Flub? Restart the whole take. Do not splice lines.

## Record

- Quiet room, mic 15–20 cm away, slightly off-axis.
- 48 kHz WAV ideal; clean M4A/MP3 acceptable. Raw audio only.
- One second of silence at the start and end.
- No music, no noise reduction, no editing.
- Three takes; send the best. `data/voice/` is gitignored.

Save as:

```
data/voice/owner-take-3min.wav
```

## What I do with it

1. Trim only the head/tail; keep the take continuous.
2. Normalize to −16 LUFS and remove low rumble.
3. Fit to 179.000 s with at most a ±2% tempo change — no per-line cutting.
4. Mux with `docs/demo-3min.mp4`, re-time captions to your read, render a preview.
5. Replace the synthetic Edge track only after you approve the preview.
