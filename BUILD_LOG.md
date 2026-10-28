# Build log

Event window: **26 Oct 2026 12:00 PM ET → 4 Nov 2026 9:00 PM ET**.
Submission: CV platform + 3-minute demo video + public GitHub repo.

This is the honest record of what was built when. The rules ask that the demo show what was built
during the event, so pre-event work is labelled instead of hidden.

## 2026-10-27 — 09:00 start: planning + first scaffold

- Read the kickoff rules and prize structure; fixed the target: Top 5 indie + $5K Best Agentic Use-Case.
- Chose the project (ONLY YOU) and wrote the 7-day plan and the 3-minute video shot list.
- Set up the repo plan and the Meta Model API environment (`.env.example`, smoke script).

## 2026-10-28 — build continued

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

**Reproducibility + upload kit**
- Fresh clone reproduces the benchmark in **9.8 s** with identical key numbers (latencies vary, as wall
  clocks do); `results/` regenerated so the committed JSON includes latency and model metadata.
- `docs/youtube-upload.md`: title, description, chapter markers, tags, settings for the 3-minute video;
  `docs/img/thumb.png` (1280×720) is the thumbnail.

**CI**
- `.github/workflows/ci.yml`: tests + demo + `tools/audit.py` on every push (installs poppler, ffmpeg,
  tesseract, imagemagick). README explains the workflow.

**Public repo + merchant verification + landing page**
- GitHub repo published and pushed incrementally: <https://github.com/sushant-me/only-you>; CI green
  (tests + demo + self-audit) on every push.
- **"Verify at merchant"** button in the mandates panel: a merchant-side offline Ed25519 check
  (`POST /api/merchant-verify`), showing `MERCHANT VERIFIED` or the rejection reason. 3 new tests.
- GitHub Pages landing page with the embedded 2:55 demo: <https://sushant-me.github.io/only-you/>.

**Receipt hardening (second-order injection + tamper evidence)**
- `clean_for_display()`: receipt-derived text is stripped of control characters, `<`/`>` neutralised,
  whitespace collapsed, length bounded — safe in any rendering context.
- `ReceiptLedger.ledger_context()`: the model-facing view labels ledger entries as **DATA, never
  instructions**, one `- [id] …` line per receipt.
- `tests/test_ledger_safety.py`: edit an amount → signature and chain both fail; malicious payee →
  single-line answer with no markup; every context line under the DATA header.
- `docs/ledger-safety.md` documents the threat, defences, tests and residual risk; limitations item 6
  updated.

**End-to-end HTTP test + architecture**
- `tests/test_web_e2e.py`: drives the actual demo server over HTTP — reset → mandate → invoice paid →
  look-alike invoice refused → poster blocked → ledger answer → agentic task → merchant verification.
  Proves the judge's path works, not just the objects (0.5 s).
- README and the landing page now show the architecture (inputs → provenance labels → gate → receipts)
  with one diagram; the model-never-executes line is explicit.

**OCR robustness (deskew)**
- Scene OCR now tries the raw image and an auto-deskewed, grayscale, auto-levelled copy, keeping the
  higher-confidence read. Re-measured on the same 35 synthetic signs: detection **94.3% → 100%**,
  mean CER **9.4% → 1.7%** (rotated 60% → 100%); weakest condition is occlusion (9.8% CER).
- Pipeline unchanged by construction: **0/35 executed**, receipts **24/35 → 27/35** (evidence coverage
  68.6% → 77.1%). Enforcement does not depend on OCR quality; only the evidence surface does.
- Limitations item 9 reworded honestly: the corpus is rendered, not camera-captured.

**Muse Spark real-model runs (key arrived)**
- Found the endpoint (`https://api.meta.ai/v1`), listed models (muse-spark-1.3, muse-wonder-1.0,
  sam-3.1, muse-voice-transcribe-1.0, muse-image-1.0) and made the first real call.
- `.env` auto-loading (`onlyyou/env.py`) so `make web` and `make bench-meta` use the key without exports.
- **Run 1 — general corpus (20 attacks / 20 benign, `results-real/`):** 195 calls, 319k completion tokens.
  Muse Spark's alignment dominates: **0% executed on every arm**, including undefended; the gate's cost is
  false refusals (D 5%, C 10%) and it files 36/36 verified receipts; p50 6.8 s (D).
- **Run 2 — document/confused-deputy (8 attacks / 12 benign, `results-real-doc/`):** 115 calls, 261k
  tokens. When the owner asks to pay and the document supplies the payee: **A 25%, B 37.5%, C 50%,
  D 0%** executed; 0% false refusals; 18/18 receipts; p50 10.7 s.
- `.env` is gitignored; the key is never committed or printed. `make test` forces the simulated model
  so the suite stays offline.

**Muse Wonder scene reader**
- `src/onlyyou/scene_muse.py`: reads a camera frame through **Muse Wonder** (multimodal chat), returns
  text + approximate pixel boxes, and never promotes scene text to authority (still labelled SCENE).
  Tesseract remains the offline fallback; `/api/frame` reports which reader answered.
- Measured on 15 synthetic signs (clean, rotated 8°, low-contrast): detection **100% (15/15)**,
  mean CER **0.0%**, ~8 s per call including render. `results/scene-muse.json`, `tools/muse_scene_eval.py`.
- 4 new tests for parsing/fences/fallback/missing-key. Demo shows three Meta models now: Muse Spark
  (agent), Muse Wonder (scene), with muse-image available for assets; SAM 3.1 still not integrated.

**Source attribution hardening + recording check**
- The real model sometimes cited a document text or an invented id as `source_id`, so the gate denied
  the *owner's* invoice with `R0-unknown-source`. `MetaModelClient.propose()` now lists the valid label
  ids in the prompt, validates the answer, and makes one repair call fixing only `source_id`.
- `Agent` now attributes invoice arguments to the document that supplied them (`arg_source`), so the
  receipt shows "instruction: owner, arguments: document" even when the model omits it.
- Pre-recording check against the live demo (Muse Spark, temperature 0), two full runs:
  invoice executed under R6 both times; attacker invoice, poster, TV and hidden-page text blocked every
  time; beat latency 3–16 s. 2 new tests (source repair, argument attribution); 104 total.
- `_default_model()` refuses the live model under `unittest`, so the suite can never hit the API.

**Recording kit + model badge**
- Header badge shows which proposer is live: green `muse-spark-1.3` or amber `simulated` (with a tooltip
  saying the gate is unchanged). One state test; 105 total.
- `docs/recording-guide.md`: setup, exact beat timings measured against the live model (invoice 6–7 s,
  look-alike invoice 10–16 s, total 45–60 s), capture commands, export, failure modes.

**Third real run — Muse Spark contributor build**
- Same confused-deputy corpus, model `muse-spark-1.3-contributor` through the Meta Model API: 115 calls,
  145k completion tokens. **A 50% · B 37.5% · C 50% · D 0% executed; 0% false refusals; 18/18 receipts
  verified**; p50 11.9 s. The gate's result replicates on a second build; committed as
  `results-real-doc-contributor/`. Not claimed as an open-weights entry (no open-weights deployment ran).

**Judge-path smoke in CI**
- `tools/smoke_web.py` starts the real `onlyyou web` server, waits for `/api/state`, then drives reset →
  mandate → invoice (executed) → look-alike invoice (refused) → ledger answer → merchant verification,
  asserting each. `make smoke-web` runs it locally; CI runs it after the demo. Unit tests import objects;
  this proves the command a judge types actually serves the demo.
- `make judge` now includes the smoke, so one command covers tests, server, and self-audit.

**Demo server hardening**
- `MAX_BODY` 8 MB with 413, negative/bogus Content-Length 400, dotfile and path-traversal 403,
  extension allowlist, `X-Content-Type-Options: nosniff` on every response.
- 6 new tests (`tests/test_web_hardening.py`); 111 total. The demo is a product surface, not a toy server.

**Voice-over path + Omni-Video feasibility**
- `make voice VOICE=…` normalises a narration track (loudnorm, 48 kHz) and muxes it onto the 2:55 captioned
  cut, padded/trimmed to 175 s; output gitignored. Verified with a test tone: 175.000 s, AAC mono.
- `docs/omni-video.md` records why Omni-Video 2 cannot run locally (6 GB RTX 4050 vs 80 GB recommendation,
  no torch/pip, 14 GB RAM) and what it is safe to use it for (atmospheric B-roll, never diffusion-edited UI
  footage, never voice).
- Report corrected to three real runs (195/115/115 calls); open-weights category explicitly not claimed.

**API validation fix (found by malformed-input sweep)**
- `/api/mandate` with `max_amount: "lots"` raised inside the handler and **dropped the connection**.
  Mandate input is now validated (integer, positive, at least one payee) and the handler maps
  `ValueError/TypeError/KeyError` to **400 JSON**, other exceptions to **500 JSON** — the connection never
  dies on a malformed request.
- `/api/frame` no longer returns raw tesseract stderr; it returns `could not read image`.
- 4 regression tests (115 total).

**Spoken commands with Muse Wonder audio-in**
- Discovered while testing the owner's mic sample: `muse-wonder-1.0` accepts `input_audio` and returns a
  transcript. Added `src/onlyyou/voice_muse.py`, `/api/voice/transcribe`, and a **🎙 Speak a command** button
  that records 4 s, transcribes with Muse Wonder, and fills the composer.
- The transcript is still text through the voice check and the gate — transcription is not verification.
- Verified on the owner's 20 s sample (transcript returned verbatim). 4 new tests; 119 total.

**Submission preflight**
- `make preflight` (`tools/preflight.py`) checks the live page, every video/PDF/SRT/thumbnail (HTTP 200 +
  bytes), the repo is public, `.env` untracked, and every submission file exists. Full run: all pass.
- Wired into the submission checklist and README; run it immediately before pasting the form.

**Two-pass voice mux**
- `tools/mux_voice.py`: measures the narration (loudnorm pass 1), then applies the measured values
  (pass 2) while copying the video stream, padding/trimming to 175 s. Tested on the owner's sample:
  output 175.000 s, integrated −17.1 LUFS (gated, includes trailing silence), AAC 160k.

**Spend-aware mandates + revoke-all**
- Backend: `MandateLedger.refund()`; undo restores the budget; receipts record `remaining_after`;
  merchant verification returns consumed/remaining; `/api/mandate/revoke-all` kills every delegation
  while keeping receipts.
- UI: mandate card now shows a spend bar (`spent / remaining of cap`), a live count on the **revoke all**
  button, and the merchant toast reports the remaining budget.
- 3 new tests (undo refund, revoke-all, merchant remaining); 122 total.

**CI flake fix: browser probe**
- One CI run failed because the Chromium computed-style probe timed out on a slow runner (60 s) during
  `test_bench_modes`. Unit tests do not need to re-measure the browser labeler — the committed benchmark
  is the evidence — so `make test` and the audit's test subprocess now set `ONLYYOU_SKIP_BROWSER=1`.
  Real `make bench` still runs Chromium, with `--disable-dev-shm-usage` added.
- Test suite drops from ~75 s to ~10 s on CI and no longer depends on a browser.

**Tests:** 136 pass (`make test`).

**Next:** first real Muse Spark call (`make smoke --call`), then `make bench-meta --limit 5` and the full
real-model benchmark. The only missing input is `META_API_BASE` / `META_API_KEY` / `MUSE_MODEL`.

## Template for the remaining days

```
## 2026-10-29 — <one line theme>

- What was built / changed
- Evidence: command, screenshot, benchmark result
- What broke / what is next
```
