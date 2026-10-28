# Voice study — the channel check, measured

The demo's voice channel is an MFCC enrollment + distance check. It is **not anti-spoofing**, and the
failure list says so. This page is the reproducible harness for putting real numbers on it.

## Run it

```bash
# one folder of owner clips (same person, a few takes), one folder of impostor clips
python3 tools/voice_study.py --owner data/voice-study/owner --impostors data/voice-study/impostors
# or: make voice-study
```

Accepts WAV/MP3/M4A/FLAC/OGG (ffmpeg converts to 16 kHz mono). Writes `results/voice-study.json` with the
threshold, owner accept rate, impostor false-accept rate, and per-clip distances.

## Protocol for a human study (10–15 people, consented)

1. Quiet room, same phone/laptop mic, one take each: *"The quick brown fox jumps over the lazy dog. Pay
   the electrician up to five thousand rupees today."*
2. Owner: 3 clips at normal/quiet/slower pace. Impostors: one clip each, no coaching.
3. All participants consent to their voice being used for this evaluation; do not commit raw audio from
   people who did not consent. Commit only the JSON summary.
4. Report owner accept rate and impostor false-accept rate, plus the distances so the threshold can be
   audited. A cloned voice is expected to pass — do not claim otherwise.

## Measured so far — **synthetic TTS study** (not human)

Generated with Edge neural voices; owner = `en-US-AndrewNeural` at three rates, impostors = six other
voices reading the same sentence. This checks the harness and the embedding, **not** human speaker
accuracy.

| Metric | Result |
|---|---|
| Owner clips accepted | **3/3** (distances 0.005–0.009; threshold 0.060) |
| TTS impostors rejected | **6/6** (distances 0.130–0.247; false-accept rate **0.0%**) |
| Human impostors | **unmeasured** — needs the consented recordings above |

Caveats: synthetic voices differ from human voices (different channel characteristics), the sample is tiny,
and the threshold is derived from the owner's own spread. The result says the harness works and TTS voices
are separable at this threshold; it does not say a human stranger is rejected.

## Why this matters for the pitch

- The honest claim becomes: **the channel is real, its human accuracy is being measured**, and the
  signed sensor envelope already closes the cheap forgery path (**6/6 → 0/6**).
- Anti-spoofing (liveness/proximity) is the named next layer, not a hidden gap.


## Muse Voice Transcribe (real Meta ASR)

The demo transcribes spoken commands with **Muse Voice Transcribe** (`POST /v1/asr/transcribe`), not a
local guess; Muse Wonder is the fallback. Reproduce:

```bash
make asr-check          # data/voice-study/asr-sample.wav -> results/voice-asr.json
```

Measured transcript for the committed sample: **"Pay the electrician electrician 4,500 rupees."** —
model `muse-voice-transcribe-1.0`. Note the duplicated word: ASR is imperfect, and the transcript is still
only *text* — it must pass the voice check and the gate like typed input.


## End-to-end spoken command (real ASR → voice check → gate)

`make voice-e2e` runs the full path on the committed sample:

| Step | Result |
|---|---|
| Muse Voice Transcribe | `muse-voice-transcribe-1.0` → "Pay the electrician electrician 4,500 rupees." (one ASR error) |
| Voice check | accept, distance **0.0** vs threshold 0.06 |
| Constitution + mandate | **executed · R6-mandate** |
| Receipt | written (signature prefix `5520f8ed6c9385c5`) |

The transcript is imperfect and still only *text*: it must pass the voice check and the gate, exactly like
typed input. Artifact: `results/voice-e2e.json`.
