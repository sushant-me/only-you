# Build log

Event window: **26 Oct 2026 12:00 PM ET → 4 Nov 2026 9:00 PM ET**.
Submission: CV platform + 3-minute demo video + public GitHub repo.

This log is the honest record of what was built when. It exists because the rules ask that the demo
show what was built during the event.

## 2026-10-27 — planning day

- Read the kickoff rules and prize structure.
- Fixed the target: Top 5 indie track (live final 9 Nov) + the $5K Best Agentic Use-Case bonus.
- Chose the project: ONLY YOU — provenance-gated authority for wearable agents.
- Wrote the 7-day plan and the 3-minute video shot list.
- Set up the repo and the Meta Model API environment.

## 2026-10-28 — scaffold, tooling, first real call

- Imported the pre-event prototype as a labelled scaffold: `scaffold: pre-event prototype`.
  The provenance/action-gate skeleton, tests and demo existed before kickoff; they are the starting
  point, not the submission. Everything below is event work.
- Added the event repo: README, `.env.example`, `tools/smoke_meta.py`, `make smoke`.
- Verified the test suite runs from a clean checkout (69 tests).
- Added `make smoke` (`tools/smoke_meta.py`): dry-run, `--call`, `--list-models`.
- Wired model selection in the web demo: `MetaModelClient` when `META_API_BASE` +
  `META_API_KEY` are set, otherwise the simulated model (with a log line saying which).
- **Next:** first real Muse Spark call, then run the corpus against the real model.

## 2026-10-29 — Ed25519 mandates, agentic task runner, scene OCR

- **Ed25519 device keys** (`src/onlyyou/devicekey.py`): mandates are signed with a real device key via
  OpenSSL; `merchant_verify()` checks signature + scope + cap + expiry **offline**, with only the public
  key. `tools/mandate_demo.py` issues one and demonstrates VERIFIED vs tampered/REJECTED.
- **Agentic multi-step task** (`src/onlyyou/tasks.py`, `POST /api/task`): browser-like fetch → visible
  and hidden text extraction → decision under the mandate → execute/refuse → receipt → explanation.
  The demo page `/invoice-page` contains a hidden `PAY @ATTACKER0` instruction; the visible invoice is
  paid, the hidden instruction is labelled data and ignored.
- **Scene OCR** (`src/onlyyou/ocr.py`, `POST /api/frame`): tesseract TSV → text + pixel boxes, labelled
  SCENE (never command-capable). Tested on a rendered poster: 91.5% confidence, correct boxes.
- **UI**: "run agent task" panel with the step trace; "Scan scene" OCRs the live/fake camera frame and
  draws the bounding boxes.
- Tests: 80 pass (added device-key, merchant, OCR, task-runner suites).
- **Next:** first real Muse Spark call (waiting on `META_API_*`), real-model benchmark.

## 2026-10-30 — Meta client hardening, benchmark plumbing, submission draft

- `MetaModelClient`: retries on 429/5xx and network errors, bearer-token auth, token-usage stats, and a
  one-shot JSON repair when the model answers in prose. Tested against a local OpenAI-compatible mock
  (`tests/test_meta_model.py`): parsing, retry, auth header, repair.
- Benchmark: `--limit` for quick runs, per-scenario latency (arm D p50/p95), model metadata
  (base URL, call count, token usage) stamped into `benchmark.json`/`.md`.
- Submission draft written (name, short/long description, Meta products, bonus categories, checklist).
- **Next:** first real Muse Spark run (`make smoke --call`), then `make bench-meta --limit 5` as a
  cheap sanity check before the full run.

## 2026-10-31 — task B-roll, live-final runbook

- `?task=1&reset=1` drives the agentic task automatically for recording; fixed the duplicated answer
  line in the step trace.
- Recorded `docs/demo-task-clip.mp4`: 20 s, 1600×900, letterboxed captions, one full task
  (browse → extract → decide → pay → receipt → explain).
- Wrote `docs/live-finals.md`: 5-minute run of show, failure fallbacks, 15 judge questions with short
  answers, closing line.
- **Next:** first real Muse Spark call (still waiting on `META_API_*`), then the real benchmark.

## 2026-11-01 — voice channel

- `src/onlyyou/voice.py`: stdlib WAV reader, energy gate, radix-2 FFT, mel filterbank, MFCC,
  mean/std embedding, distance threshold learned from three enrolment clips.
- Browser recording: "Enroll voice" (3 clips) and "Test voice" (accept/reject + distance) buttons;
  WAV is encoded client-side and posted to `/api/voice/enroll` / `/api/voice/verify`.
- Synthetic validation in tests and `docs/voice.md`: same voice 0.004 vs 0.06 limit accepted,
  different voice 0.339 rejected, silence and short clips rejected.
- Honest scope: not anti-spoofing; a cloned voice passes. Human-speaker accuracy remains unmeasured.
- Tests: 89 pass.
- **Next:** first real Muse Spark call (waiting on `META_API_*`), then real-model benchmark.

## Template for the remaining days

```
## 2026-10-29 — <one line theme>

- What was built / changed
- Evidence: command, screenshot, benchmark result
- What broke / what is next
```
