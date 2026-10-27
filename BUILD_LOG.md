# Build log

Event window: **26 Oct 2026 12:00 PM ET → 4 Nov 2026 9:00 PM ET**.
Submission: CV platform + 3-minute demo video + public GitHub repo.

This is the honest record of what was built when. The rules ask that the demo show what was built
during the event, so pre-event work is labelled instead of hidden.

## 2026-10-27 — planning

- Read the kickoff rules and prize structure; fixed the target: Top 5 indie + $5K Best Agentic Use-Case.
- Chose the project (ONLY YOU) and wrote the 7-day plan and the 3-minute video shot list.
- Set up the repo plan and the Meta Model API environment (`.env.example`, smoke script).

## 2026-10-28 — build day

A single long session. The pre-event prototype was imported first as a labelled scaffold, then every
item below was built on top of it.

**Scaffold**
- `scaffold: pre-event ONLY YOU prototype` — provenance labels, action gate, constitution, mandates,
  receipts, benchmark harness, web demo, tests. Starting point, not the submission.

**Model + benchmark**
- `make smoke` (`tools/smoke_meta.py`): dry run, `--call`, `--list-models`. Never prints the key.
- Demo model selection: `MetaModelClient` when `META_API_BASE`/`META_API_KEY` are set, simulated
  otherwise, with a log line saying which.
- `MetaModelClient`: retries on 429/5xx and network errors, bearer auth, token-usage stats, one-shot
  JSON repair when the model answers in prose. Tested against a local OpenAI-compatible mock.
- Benchmark: `--limit` for quick runs, arm-D latency p50/p95, model metadata (base URL, calls, tokens).

**Mandates**
- `devicekey.py`: Ed25519 device keys via OpenSSL; mandates sign with the device key.
- `merchant_verify()`: offline verification with only the public key (signature + scope + cap + expiry).
- `tools/mandate_demo.py`: issues a mandate and shows VERIFIED vs tampered/REJECTED.

**Agentic task**
- `tasks.py` + `POST /api/task`: browse → extract visible and hidden text → decide → gate → execute →
  receipt → explain. Demo page `/invoice-page` hides a `PAY @ATTACKER0` instruction; the visible invoice
  is paid, the hidden one is labelled data and ignored.
- `?task=1&reset=1` drives it automatically for recording; step-trace dedupe and ledger refresh.

**Perception**
- `ocr.py` + `POST /api/frame`: tesseract TSV → scene text + mask boxes, labelled SCENE (never a
  command). Rendered-poster test: 91.5% confidence.
- `voice.py`: WAV → energy gate → FFT → mel/MFCC → mean/std embedding → distance threshold learned from
  three enrolment clips. Browser "Enroll voice"/"Test voice"; `/api/voice/enroll|verify|reset`.
  Synthetic validation: same 0.004 vs 0.06 accepted, different 0.339 rejected. Not anti-spoofing.

**Media + docs**
- `docs/video-3min.md`: 3-minute shot list, VO script, export and upload steps, 45 s X cut.
- `docs/demo-task-clip.mp4`: 20 s captioned letterboxed walkthrough of the task trace.
- `docs/live-finals.md`: 5-minute run of show, failure fallbacks, 15 judge questions.
- `SUBMISSION-DRAFT.md` (repo parent): CV-platform fields and checklist.
- `docs/voice.md`, README, limitations updated.

**Pitch deck**
- `docs/pitch-event.md` refreshed with the event-built features (voice channel, Ed25519 mandates, agentic
  task, updated evidence) and rendered to `docs/pitch.pdf` (9 slides, 16:9).

**Fallback video**
- `docs/demo-fallback.mp4`: 82 s, 1600×900, silent, captioned — title card → mandate → invoice →
  look-alike refusal → poster → TV → hidden page → ledger → agentic task trace → evidence → end card.
  Recorded from the real UI with `?script=full&fakecam=1` and `?task=1&reset=1`; assembled with ffmpeg
  (letterboxed caption bar). Use if screen recording fails; add the voice-over later.

**Self-audit**
- `tools/audit.py` (`make audit`): tests, benchmark numbers vs the docs, relative links, secret scan,
  required artifacts, PDF page counts and video durations. Run it before submitting.

**Vertical X clip**
- `docs/demo-x-vertical.mp4`: 45 s, 1080×1920, captioned vertical cut for the $20K Most Viral
  Project prize — title → invoice → look-alike refusal → poster → TV → task → evidence → close.
  Post it on X; likes/reposts/comments close 8 Nov, 11:59 PM ET.

**Submission kit**
- `docs/submission-checklist.md`: publish → record → submit → bonuses, with the pre-flight `make audit`.
- `docs/x-post.md`: three post variants, thread structure, posting checklist for the viral prize.
- Report footer placeholders removed; stale pre-event `pitch.md` removed (the deck source is
  `pitch-event.md`); `report.pdf` and `pitch.pdf` rebuilt.

**Open-weights + outreach**
- `--model open` + `make bench-open LIMIT=10`: the evaluator can run on a Muse Glimmer / Muse Spark
  Open OpenAI-compatible endpoint (`OPEN_WEIGHTS_*`); the trust layer stays local.
- `docs/open-weights.md`: deploy, wire, measure, fallbacks, honesty rules for the $10K category.
- `docs/outreach.md`: 12 contacts, three message variants, follow-up cadence, tracker.

**Model-mode integration tests**
- `tests/test_bench_modes.py`: proves `bench --model meta` and `bench --model open` construct the client,
  make calls, and write a report with model metadata against a mock OpenAI-compatible endpoint. The
  plumbing is verified; only the credential is missing.

**3-minute demo video**
- `docs/demo-3min.mp4`: **2:55**, 1600×900, silent + captioned — the full submission video: title → problem
  (Meta quote) → the gap → mandate → invoice → look-alike refusal → poster → TV → hidden page → ledger →
  agentic task trace → evidence → what breaks it → why Meta → close. Assembled from the real UI and
  cards; a voice-over can be laid over it or the 3-minute script used to re-record.

**Tests:** 91 pass (`make test`).

**Next:** first real Muse Spark call (`make smoke --call`), then `make bench-meta --limit 5` and the full
real-model benchmark. The only missing input is `META_API_BASE` / `META_API_KEY` / `MUSE_MODEL`.

## Template for the remaining days

```
## 2026-10-29 — <one line theme>

- What was built / changed
- Evidence: command, screenshot, benchmark result
- What broke / what is next
```
