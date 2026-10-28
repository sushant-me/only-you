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
- `docs/demo-3min.mp4`: **2:59**, 1600×900, silent + captioned — the full submission video: title → problem
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
- GitHub Pages landing page with the embedded 2:59 demo: <https://sushant-me.github.io/only-you/>.

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
- `make voice VOICE=…` normalises a narration track (loudnorm, 48 kHz) and muxes it onto the 2:59 captioned
  cut, padded/trimmed to 175 s; output gitignored. Verified with a test tone: 179.000 s, AAC mono.
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
  output 179.000 s, integrated −17.1 LUFS (gated, includes trailing silence), AAC 160k.

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

**Signed webhook deliveries + share cards**
- Alerts now carry `X-OnlyYou-Signature: sha256=<hmac>` over the raw body and `X-OnlyYou-Event`; the existing
  delivery test asserts both, so a SIEM can reject unsigned requests. Playground/landing now have
  OpenGraph/Twitter metadata; the X clip's end card was refreshed to 172 tests.

**Narrated demo (synthetic draft)**
- Generated a 175.0 s narration track from `docs/narration-script.md` with Edge `en-US-AndrewNeural`,
  aligned per section, loudnorm to -16 LUFS, and muxed as AAC into `docs/demo-3min.mp4`. The submission is
  never silent; a human recording can replace the track with `make voice VOICE=...`. End cards at 172 tests.

**Docker + deploy docs**
- `Dockerfile` (python:3.12-slim + tesseract/qrencode, healthcheck on `/api/state`, port 8000),
  `docker-compose.yml`, `make docker` / `make docker-run`, `docs/deploy.md`. Verified locally: image builds
  and serves `/`, `/api/state`, `/docs` on a mapped port. No test count change (172).

**Security hardening + judge-ready landing**
- All responses now carry `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, a camera/mic
  `Permissions-Policy`, COOP and CORP (asserted in the existing hardening test, no new test count).
- Added `SECURITY.md` (private advisory path, demo-only list, defensive details) and compressed the
  landing gallery to 720px JPEGs (~1.7 MB → ~350 KB total). 172 tests.

**Browser audit verifier**
- `docs/verify.html`: paste an audit export (or load the committed sample) and re-check the HMAC chain and
  Ed25519 mandate signatures with WebCrypto — no server, no Python. The Python verifier and the browser
  verifier are cross-checked: the export test now also verifies `docs/audit-sample.json`. 172 tests.

**Judge-experience polish**
- Landing video now has a WebVTT captions track (`docs/demo-3min.vtt`, generated from the SRT); acceptance
  doc count fixed; hiring memo updated to three real runs and the full current feature surface; pitch deck
  refreshed to 10 slides, adding "it doesn't just block — it proves" and merchant checkout.

**Post-build real-model reproduction**
- Re-ran the harness against live Muse Spark after the final feature work: 8 attacks / 8 benign, all arms
  0% executed, 16/16 receipts verified, chain intact, 99 calls, p50 3.1 s. Committed to
  `results-real-verify/` (general corpus reproduction, not a new security claim).

**Honest-limits refresh + report**
- `docs/limitations.md` now names 16 attacks, adding scheduled instructions, sub-mandate widening, policy
  import, webhook spoofing, an exposed demo server and synthetic narration — with status per row.
- `docs/report.md`/PDF updated: four real runs (including the final-code reproduction), rebuilt to 2 pages.

**One-page executive brief**
- `docs/brief.md` → `docs/brief.pdf` (1 page): problem, three primitives, evidence table, commercial why,
  30-second try path, honest line, and the ask. Linked from the landing page, README and submission
  sheet; `make brief` regenerates it.

**Press / viral kit**
- `docs/press.md`: boilerplate at 1/50/150 words, four headline options, committed stats, image table with
  alt text, links. Three 1200×675 share cards (`img/x-stat.png`, `x-quote.png`, `x-try.png`) generated for
  the viral category; X post updated with attachments, alt text and cross-post guidance.

**Legal / credits + outreach links**
- `NOTICE.md`: model and asset provenance, optional system tools and licences, data statement, attribution.
- Outreach message updated with the playground, browser verifier and one-page brief; README links NOTICE.

**Judge-first README + link guard**
- README opens with a "Start here" row (narrated demo, playground, brief, repo, live page) and badges for
  tests, self-audit, Docker and licence.
- `tools/check_links.py` + `make links` + a CI step fail the build if a local href/src in the static pages
  points at a missing file (25 references checked).

**Live-final runbook refreshed**
- `docs/live-finals.md` now matches the current product: merchant verification, QR/verify page, browser
  audit verifier, delegation/recurring/scheduled answers, a 3-minute condensed cut, static-asset failure
  fallbacks and 15 current Q&A answers.

**Fresh demo/video assets**
- Captured the current UI running on the real model (`demo-live-muse.png`: 4 blocked, 1 allowed, 5
  receipts, chain OK) and regenerated the video contact sheet from the narrated cut.

**Frontier adapter + measured latency + README reframe (feedback round 1)**
- `src/onlyyou/frontier.py` + `--model frontier` + `make bench-frontier`: one OpenAI-compatible adapter for
  OpenAI / Gemini / Claude / OpenRouter / local Ollama; no gate changes. No frontier key with credit was
  available (DeepSeek key 402; GitHub token lacks Models access), so no frontier run is claimed — `docs/frontier.md`
  states this and gives the exact command for when a key exists.
- Measured and published the local latency budget (`results/latency.json`, `make latency`): constitution
  rules 0.001 ms p50; dry-run path 4.3 ms; local HTTP command 12.8 ms; OCR 156 ms; model call dominates.
- README now reframes the alignment confound (0% undefended is the first line; confused deputy is the gap),
  names the cloned-voice failure with the signed-bus next step, and opens with a 26 s attack-blocked GIF.

**Voice study harness + synthetic result (feedback round 2)**
- `tools/voice_study.py` / `make voice-study`: owner vs impostor folders → threshold, owner accept rate,
  impostor false-accept rate, per-clip distances (`results/voice-study.json`).
- Ran a synthetic TTS study: owner 3/3 accepted, **6/6 TTS impostors rejected** (0% false accept). Honest
  scope: synthetic voices, not humans; `docs/voice-study.md` gives the consented human protocol.

**SAM 3.1 probe (honest negative)**
- `sam-3.1` is listed by `/v1/models` but is not available on `/v1/chat/completions`; `/v1/responses`
  accepts the image (`images_processed: 1`) and returns an **empty message with 0 tokens** on this key.
  No mask payload or documented format was found, so scene grounding stays OCR-based; added to the failure
  list rather than claimed.

**Frontier experiment runner + judge-first README**
- `tools/frontier_eval.py` / `make frontier-eval`: arms A vs D on the committed confused-deputy corpus,
  provider-agnostic (API key or local Ollama), writes results-frontier/benchmark.json + md.
- README reordered for a judge: one-liner → 30-second GIF → evidence table → one-command run → assets.

**Local model through the frontier adapter (integration, not a frontier claim)**
- Ran `make frontier-eval` against `llama3.2:3b` in Ollama: undefended arm paid **2/2** injected invoices;
  the full gate blocked all injected payments (**0/2**) with 4/4 verified receipts — but also blocked 2/2
  benign cases (`R0-unknown-source`) because the small model misattributed provenance. Documented honestly
  in `docs/frontier.md`; artifacts in `results-local-llama/`. A frontier key is still needed for the
  actual headline experiment.

**Cross-model audit bundle**
- `tools/cross_model_bundle.py` / `make cross-model`: same constitution and gate run under Muse Spark and a
  local Llama 3.2 3B, one bundle per model sharing a device key; verifier extended to `only-you-cross-model/1`
  and the browser page verifies both in one pass (`VERIFIED · CROSS-MODEL`). Muse: benign executed + attack
  blocked; local model: attack blocked, benign blocked due to provenance misattribution (documented).
- Artifacts in `results-cross-model/`; `docs/cross-model.md`; landing link.

**20-second contrast clip + deck/brief cross-model slide**
- `docs/demo-contrast.mp4` (20.5 s, narrated): undefended local model pays 2/2 injected invoices →
  same model behind the gate pays 0/2 with 4/4 verified receipts → Muse Spark 25%→0% → closing line.
  Honest label: local open-weights model, frontier key still pending. Linked from README/landing/X kit.
- Deck (10 slides) now carries the cross-model audit line and the voice-study + SAM honesty lines; the
  1-page brief adds the cross-model row.

**Submission sheet + live QA refresh**
- Submission links now include the playground, browser verifier, cross-model audit, latency artifacts and
  the 20s contrast clip; "built during the event" lists the full current surface.
- Incognito-style live QA: landing, playground auto-run (3 blocked), verifier cross-model
  (`VERIFIED · CROSS-MODEL`), and all six assets return 200 on Pages.

**Frontier thesis across every submission asset**
- The pitch line "the more capable the model, the more it needs an authority layer" now opens README,
  brief, YouTube description, X post and the form answers; the deck's Why-Meta slide spells out the
  Amazon/Muse verification argument.
- Rebuilt the 1-page brief and the 10-slide deck (page counts unchanged).

**3-minute film re-cut — the contrast now opens the demo**
- Prepended a 4 s opening to `docs/demo-3min.mp4`: undefended local model **2/2 injected invoices paid** →
  same model behind the gate **0/2 paid, 4/4 receipts verified** (honestly labelled "local open-weights model",
  frontier key still pending). Narration and burned-in captions shifted +4 s; duration 175 → 179 s (still ≤3:00).
- Updated SRT/VTT (-+4 s), narration script, YouTube chapters, mux duration, audit duration check, README/brief/
  deck/"2:59" references; rebuilt the 26 s README GIF from the new timeline.

**SAM 3.1 object grounding, integrated (Meta stack: Spark + Wonder + SAM)**
- Read the public SAM docs, found the correct `/v1/responses` contract (short noun phrase + `input_image`);
  `sam-3.1` returns special-token boxes/masks. Added `src/onlyyou/sam.py` (box parser + adapter with cache),
  `make sam-check`, and wired `/api/frame` + the overlay to draw the green SAM region.
- Measured on the committed demo frame: `paper`/`document` → **1 region**; `invoice`/`receipt`/`text` → 0.
  Text-region masks are **not** claimed: mask payloads are not decoded (needs `@meta-sam/parser`); docs/sam.md
  states this and the failure-list row is updated. Tests stay 172 (parser assertions folded into the API test).

**Tests:** 172 pass (`make test`).

**Next:** first real Muse Spark call (`make smoke --call`), then `make bench-meta --limit 5` and the full
real-model benchmark. The only missing input is `META_API_BASE` / `META_API_KEY` / `MUSE_MODEL`.

## Template for the remaining days

```
## 2026-10-29 — <one line theme>

- What was built / changed
- Evidence: command, screenshot, benchmark result
- What broke / what is next
```
