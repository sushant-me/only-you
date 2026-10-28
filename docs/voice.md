# Voice channel

`src/onlyyou/voice.py` — a small, dependency-free speaker check so "only the enrolled owner's voice is
a command" is enforced by code, not assumed.

## Pipeline

```
WAV → mono 8 kHz → 32 ms frames (16 ms hop) → energy gate
    → Hann window → radix-2 FFT → 24 mel filters → log → DCT
    → 13 MFCC per frame → mean + std across frames → L2-normalise
    → Euclidean distance to the enrolment centroid
```

Enrolment uses three clips. The centroid is their mean; the threshold is
`max(0.06, 2.5 × max(self-distance) + 0.02)`, so a tight enrolment gives a tighter threshold.

## Use

```bash
make web            # http://127.0.0.1:8000
```

- **Enroll voice** — records three 1.6 s clips in the browser and posts them as WAV.
- **Test voice** — records one clip and shows `accepted`/`rejected`, the distance and the threshold.

API:

```bash
POST /api/voice/enroll   {"clips": ["<b64 wav>", "...", "..."]}
POST /api/voice/verify   {"clip": "<b64 wav>"}
POST /api/voice/reset
GET  /api/state          # includes voice.enrolled / threshold
```

## What it is, and what it is not

It is a **channel demonstrator**: the provenance rule (only a verified channel can be a command) is
enforced, and the check is real code with a measured threshold.

It is **not** an anti-spoofing speaker model. A cloned voice passes; a professional impersonator may
pass; background noise and microphone changes move the distance. The product would use the platform's
biometric speaker ID (or a trained embedding such as ECAPA) behind the same interface.

## Synthetic validation (what the tests cover)

| Check | Distance | Threshold | Result |
|---|---|---|---|
| same synthetic voice (unseen clip) | 0.004 | 0.06 | accepted |
| different synthetic voice | 0.339 | 0.06 | rejected |
| silence | — | — | rejected ("not enough speech") |
| 0.15 s clip | — | — | rejected |

These validate the pipeline, not human-speaker accuracy.

## Human study — LibriSpeech public speakers (real voices)

A reproducible public-corpus study on **LibriSpeech dev-clean** (CC BY 4.0): one speaker enrolled from
three clips; **12 different human speakers** per set, one clip each, different sentences.

| Set | Threshold | Owner | Impostor FAR |
|---|---|---|---|
| Pilot (12 speakers) | uncapped learned 0.1825 | 3/3 | **2/12 (16.7%)** |
| Pilot, same clips | **capped 0.10** | 3/3 | **0/12** |
| **Held-out (12 unseen speakers)** | **capped 0.10** | 3/3 | **0/12** |

The cap is now the demo default: `enroll()` bounds the learned threshold at **0.10** (override with
`VOICE_MAX_THRESHOLD`), so a wide enrolment spread cannot open the channel to strangers. The 0.10 value
was fixed **after the pilot but before the held-out speakers** — this is a held-out check, not a fully blind
pre-registration, and that distinction is stated everywhere the number appears. Artifacts:
`results/voice-study-human.json`, `results/voice-study-human-heldout.json`.

Sensitivity from the pilot (thresholds evaluated after seeing the pilot, exploratory):

| Fixed threshold | Owner accept | Pilot FAR |
|---|---|---|
| 0.06 | 2/3 | 0/12 |
| **0.10** | **3/3** | **0/12** |
| 0.13 | 3/3 | 1/12 |
| 0.1825 (uncapped) | 3/3 | 2/12 |

The channel is still a **channel demonstrator, not anti-spoofing**: a cloned voice passes, different-content
clips are harder than a same-phrase friend study, and the next step is a trained embedding (ECAPA) plus
liveness. But the held-out human result is now **0/12**, not 2/12.
