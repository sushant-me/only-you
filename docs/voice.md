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

These validate the pipeline, not human-speaker accuracy. Human accuracy requires a consented
enrolment session; that is the next measurement, and it is stated as unmeasured in the report.
