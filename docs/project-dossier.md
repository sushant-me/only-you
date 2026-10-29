# ONLY YOU — full project dossier
*Generated 2026-10-29 10:14 +0545 from commit `2c60ed6` (2026-10-29).*

> **Capability is solved. Authority isn’t.**
>
> Everyone is building agents that can do things. This is the one you can hand your wallet.

This dossier is generated from the repository, not written by hand after the fact: the test count, audit, benchmark tables, PDF page counts and video durations below are read at build time. `python3 tools/dossier.py` regenerates the Markdown source and this PDF.

## 1. One-page fact sheet

| Item | Value |
|---|---|
| Project | ONLY YOU — a provenance-gated authority layer for wearable agents |
| Hackathon | Meta Global AI Developer Hackathon 2026 · Indie track |
| Commit / date | `2c60ed6` · 2026-10-29 |
| Tests | Ran ? tests · self-audit ****67 passed · 0 failed**** |
| Meta models | Muse Spark 1.3, Muse Wonder 1.0, Muse Voice Transcribe 1.0, SAM 3.1, Muse Image 1.0 |
| Frontier run | DeepSeek-chat: undefended **50%** executed → gate **0%**, 0% false refusals, **18/18** receipts |
| Human voice study | owner 3/3 · **0/12 FAR** at capped 0.10 (pilot + 12 unseen speakers) |
| Repository | 291 files · 30 Python modules · 20 tools · 31 test files · ~7007 lines in `src/onlyyou` |
| Primary artefacts | 3-min film (179 s), 60 s motion cut (16:9), 60 s vertical (9:16), contrast clip, brief, report, deck, handbook, dossier |

## 2. The problem and the thesis

A wearable agent has a camera, a microphone and (soon) a wallet. The world can reach its context: a TV ad, a poster, a webpage, a look-alike invoice. Meta’s own WebMCP developer documentation says the untrusted-content hint is *“not an enforced security boundary.”* The model cannot be the boundary, because the model is what is being confused.

**ONLY YOU** makes provenance the authority boundary: only the enrolled owner’s voice is a command; scene text, page text and documents are **data**; irreversible actions need a signed, scoped, expiring mandate; every action *and every refusal* leaves a verifiable receipt. The model proposes, the gate decides, the ledger proves.

## 3. Authority model

| Channel | Example | Can it command? |
|---|---|---|
| voice (enrolled owner) | “pay the electrician 4,500” | yes, after speaker check |
| scene | poster, TV ad, camera text | no — data only |
| document | invoice, PDF, email | no — data only (can supply payee/amount) |
| web | page text, DOM, hidden text | no — data only |
| model | proposal / tool call | no — proposal, not authority |

| Rule | Decision |
|---|---|
| `R0-source-not-authoritative` | deny an action whose cause is not an authoritative channel |
| `R1-payee-not-contact` | deny paying an unknown payee |
| `R2-payment-over-limit` | ask above the per-action limit |
| `R3` / `R4` / `R5` | confirm unlock/delete, no file exfiltration |
| `R6-mandate` | allow only inside a valid signed mandate (payee, cap, expiry, remaining) |
| `R7-policy-change` | policy edits are themselves receipted and signed |

Mandates are Ed25519-signed statements (owner key → agent key, payees, max, expiry, optional period/sub-limit/parent). A merchant verifies one offline with only the public key. Receipts form an HMAC chain; the audit export contains chain head, spend totals, mandates and public key; `tools/verify_audit.py` and the browser verifier recompute them offline.

## 4. Feature surface

- **Provenance routing** — voice / scene / document / web / model labels; only owner voice commands.
- **Deterministic constitution** — editable at runtime, dry-run what-if, each policy edit receipted (`R7`).
- **Signed mandates** — scoped, expiring, per-action cap, recurring period, sub-limits, recursive sub-mandates, revoke-all.
- **Merchant checkout** — offline mandate verification (signature, payee, cap, remaining) before charging; no platform call.
- **Receipts** — every action and refusal; hash chain; per-receipt verify pages; QR codes; ledger search/CSV; undo.
- **Signed audit export** — CLI verifier and browser WebCrypto verifier; tampering one field fails verification.
- **SIEM alerts** — HMAC-signed deliveries with retries; sub-limits; scheduled standing instructions.
- **Agentic task runner** — browse, extract visible + hidden text, decide under mandate, receipt, explain.
- **Scene channel** — Muse Wonder text + boxes; tesseract fallback; SAM 3.1 object grounding with live overlay.
- **Voice channel** — MFCC enrollment/verification, liveness caveats, Muse Voice Transcribe, end-to-end spoken command.
- **Frontier adapter** — one OpenAI-compatible adapter (OpenAI, Gemini, Anthropic, DeepSeek, OpenRouter, Ollama); A/D experiment.
- **Cross-model audit** — same gate/receipts/device key for Muse Spark + DeepSeek, verified in the browser.
- **Demo surfaces** — live UI, no-install playground, merchant page, OpenAPI/Swagger, Docker/compose.

## 5. The Meta stack

| Model | Role | Endpoint | Evidence |
|---|---|---|---|
| Muse Spark 1.3 | proposes actions; gate re-validates | `/v1/chat/completions` | four real runs (`results-real*/`) |
| Muse Wonder 1.0 | camera frame → text + boxes | chat completions with image | `results/scene-muse.json` (15/15, 0.0% CER) |
| Muse Voice Transcribe 1.0 | spoken command → transcript | `POST /v1/asr/transcribe` | `results/voice-asr.json`, `results/voice-e2e.json` |
| SAM 3.1 | object grounding (box) | `POST /v1/responses` | `results-sam/sam.json` (`paper` → 1 box) |
| Muse Image 1.0 | demo posters, TV, invoice, hero | image generation | `src/onlyyou/web/fakecam-*.jpg`, `docs/img/hero.jpg` |

![SAM 3.1 paper region](img/dossier-sam.jpg)

Honest limits: SAM returns object boxes, not text masks; mask decoding is roadmap. Muse Voice Transcribe is real ASR and makes real errors; the transcript still passes the voice check and gate. The MFCC voice channel is a demonstrator, not anti-spoofing.

## 6. Evidence: confused deputy

Corpus: 8 attacks / 12 benign, channels document; model `muse-spark-1.3`.

| Arm | Architecture | Attack success | False refusals | Receipts |
|---|---|---|---|---|
| A | undefended | 25.0% | 0.0% | 0/0 |
| B | prompt-only | 37.5% | 0.0% | 0/0 |
| C | provenance-only | 50.0% | 0.0% | 0/0 |
| D | full ONLY YOU | 0.0% | 0.0% | 18/18 |

The full gate is the only arm at 0% executed, with 0% false refusals and 18/18 receipts. A contributor build reproduces the finding (A 50% → D 0%); the final-code reproduction has every arm 0%, 16/16 receipts, chain intact, 99 calls.

## 7. Evidence: general corpus and frontier

General corpus (`results-real/benchmark.json`): 20 attacks / 20 benign across ambient_audio, scene, voice, web. Muse Spark refused even undefended; every arm 0%. This is the alignment confound: alignment is the first line, not the authority layer.

| Arm | Architecture | Attack success | False refusals | Receipts |
|---|---|---|---|---|
| A | undefended | 0.0% | 0.0% | 0/0 |
| B | prompt-only | 0.0% | 0.0% | 0/0 |
| C | provenance-only | 0.0% | 10.0% | 0/0 |
| D | full ONLY YOU | 0.0% | 5.0% | 36/36 |

**Frontier A-vs-D** (`results-frontier/benchmark.json`): deepseek-chat via deepseek on the same 8 attacks / 12 benign corpus.

| Arm | Architecture | Attack success | False refusals | Receipts |
|---|---|---|---|---|
| A | undefended | 50.0% | 0.0% | 0/0 |
| D | full ONLY YOU | 0.0% | 0.0% | 18/18 |

That is the headline: the more capable/helpful the model, the more it needs the authority layer. The run took 54.1 s and 40 calls at temperature 0.

## 8. Evidence: other layers

| Test | Result | Source |
|---|---|---|
| DOM hidden-text labeler | recall 81.0%, FPR 14.3%, precision 87.2% | `results-real-doc/benchmark.json` |
| Adaptive attacker (simulated harness) | label error 80%, executed 20% | `results/benchmark.json` (simulated) |
| Forged sensor signals (simulated harness) | 6/6 without envelope → 0/6 with signed bus | `results/benchmark.json` (simulated) |
| Synthetic TTS voice study | owner 100% accepted; impostor FAR 0.0% (threshold 0.06) | `results/voice-study.json` |
| Human voice pilot (LibriSpeech) | owner 1.0 · FAR 0.0 at threshold 0.1 | `results/voice-study-human.json` |
| Human voice held-out (12 unseen) | owner 1.0 · FAR 0.0 at threshold 0.1 | `results/voice-study-human-heldout.json` |
| SAM 3.1 grounding | `paper` → 1 box(es) across 2 frame(s) | `results-sam/sam.json` |
| Muse Voice Transcribe | `Pay the electrician electrician 4,500 rupees.` | `results/voice-asr.json` |
| Spoken command end-to-end | outcome **executed** · rule `R6-mandate` · voice accept True | `results/voice-e2e.json` |
| In-process gate | constitution 0.001 ms · dry-run 4.282 ms · HTTP command 12.811 ms · OCR 156.118 ms | `results/latency.json` |

The adaptive/forged figures come from the deterministic simulated harness in `results/benchmark.json`; the real-model runs use Muse Spark and are reported separately. The label layer is the measured weak point: 81% recall means hiding techniques are missed, and the report publishes them.

## 9. Cross-model audit

| Provider | Model | Benign invoice | Look-alike invoice | Receipts |
|---|---|---|---|---|
| meta | muse-spark-1.3 | executed | blocked | 2/2 |
| deepseek | deepseek-chat | executed | blocked | 2/2 |

![Browser verifier: VERIFIED · CROSS-MODEL](img/dossier-verify.jpg)

`results-cross-model/cross-model-audit.json` is verified by the CLI and by `docs/verify.html` (WebCrypto) as **VERIFIED · CROSS-MODEL**. Both models share the device key, receipt format and verifier.

## 10. Video and presentation assets

| Asset | Type | Size / duration / pages |
|---|---|---|
| `docs/demo-3min.mp4` | 3-minute narrated film | 179.000 s · 11.2 MB |
| `docs/demo-60s.mp4` | 60-second motion cut (16:9) | 60.000 s · 11.7 MB |
| `docs/demo-60s-vertical.mp4` | 60-second vertical cut (9:16) | 60.000 s · 4.3 MB |
| `docs/demo-contrast.mp4` | 20-second contrast clip | 20.500 s · 602 KB |
| `docs/demo-fallback.mp4` | 82-second silent walkthrough | 82.000 s · 5.7 MB |
| `docs/demo-task-clip.mp4` | 20-second agentic task clip | 20.000 s · 1.2 MB |
| `docs/brief.pdf` | 1-page executive brief | 1 pages · 164 KB |
| `docs/report.pdf` | 2-page report | 2 pages · 226 KB |
| `docs/pitch.pdf` | 10-slide deck | 10 pages · 576 KB |
| `docs/handbook.pdf` | 18-page handbook | 18 pages · 549 KB |

![60-second cut storyboard](img/dossier-storyboard-small.jpg)

The 60-second cut follows the requested beat sheet: hook 0–3, quote 3–7, mandate 7–13, pay/R6 13–20, attack/R1 20–30, poster/R0 30–36, frontier 50→0 36–45, browser verify 45–52, close/CTA 52–60. Cards are held under five seconds; cursor and zoom carry the UI beats. The UI states are real captures from a live Muse Spark server; the cursor/zooms/captions are edited motion graphics. Narration is synthetic and disclosed.

## 11. Repository and commands

The repository has 291 tracked files, 30 Python modules in `src/onlyyou`, 20 tools and 31 test files (~7007 lines in the package).

| Command | What it does |
|---|---|
| `make judge` | 172 tests + 67-check self-audit + live server smoke |
| `make preflight` | live links, repo public, submission files (retries GitHub API) |
| `make web` | live demo at `http://127.0.0.1:8000/?script=full&fakecam=1` |
| `make test` | unit tests |
| `make bench` / `make bench-meta` | simulated / real Muse benchmark |
| `make frontier-eval` | A vs D on the confused-deputy corpus with any OpenAI-compatible provider |
| `make cross-model` | Muse + DeepSeek audit bundle |
| `make sam-check` / `make asr-check` / `make voice-e2e` | Meta perception checks |
| `make latency` | routing/gate/OCR/HTTP latency |
| `make brief report pitch handbook dossier` | rebuild PDF assets |
| `make thumb` | rebuild the YouTube thumbnail |

## 12. Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /` | demo UI |
| `POST /api/command` | the gate: label → propose → decide → execute/refuse → receipt |
| `POST /api/mandate` | grant a signed, scoped mandate |
| `POST /api/simulate` | dry run the constitution |
| `POST /api/frame` | scene OCR + Muse Wonder + SAM boxes |
| `POST /api/voice/transcribe` | Muse Voice Transcribe |
| `POST /api/task` | agentic task trace |
| `POST /api/export` | signed audit bundle |
| `GET /verify/<receipt>` | per-receipt verification page |
| `GET /merchant-page` | offline mandate verification |
| `GET /docs` | OpenAPI 3.1 + Swagger |

## 13. Known limitations

| Risk | Status | Next step |
|---|---|---|
| Cloned voice passes the channel check | **Open**; human FAR **0/12** at capped 0.10 (pilot + 12 unseen); uncapped pilot 2/12 | ECAPA/TDNN embedding + liveness |
| Label layer misses hiding techniques | **Open**; 81% DOM recall, 14.3% FPR | browser computed-style labeler + SAM mask decode |
| Adaptive attacker controls signals | **20% executed** in the simulated harness | liveness + proximity attestation + confirmations |
| Evidence coverage on paraphrases | **1/8 receipted** | trigger-verb classifier + always-receipt policy |
| SAM text masks not decoded | **Open**; object boxes ship | decode masks, crop text before OCR |
| ASR errors | real; duplicated word in sample | vocabulary biasing + confidence gate |
| Frontier result one provider | DeepSeek shipped | add GPT/Gemini/Claude key and re-run |

The full 17-row failure list with evidence is in `docs/limitations.md`.

## 14. Submission readiness

| Item | Status |
|---|---|
| Repo public, logged out | yes |
| Tests / audit / CI | 172 / 67 of 67 / green |
| Video | 3-minute film 179 s; 60 s cuts 16:9 and 9:16; SRTs committed |
| Live playground | `sushant-me.github.io/only-you/playground.html` |
| Browser verifier | `sushant-me.github.io/only-you/verify.html` |
| Docs | brief 1 page, report 2, deck 10, handbook 18, dossier this file |
| Remaining user action | upload YouTube unlisted + submit the form (`SUBMIT-NOW.md`) |

## 15. Generated file inventory

| File | Bytes |
|---|---|
| `docs/demo-3min.mp4` | 11.2 MB |
| `docs/demo-3min.srt` | 2 KB |
| `docs/demo-60s.mp4` | 11.7 MB |
| `docs/demo-60s.srt` | 1 KB |
| `docs/demo-60s-vertical.mp4` | 4.3 MB |
| `docs/demo-60s-vertical.srt` | 1 KB |
| `docs/demo-contrast.mp4` | 602 KB |
| `docs/brief.pdf` | 164 KB |
| `docs/report.pdf` | 226 KB |
| `docs/pitch.pdf` | 576 KB |
| `docs/handbook.pdf` | 549 KB |
| `docs/img/youtube-thumb.jpg` | 48 KB |
| `docs/img/attack-blocked.gif` | 2.5 MB |

## 16. Recent commits

- `2c60ed6 feat: generated full project dossier PDF (with visuals)`
- `b0870d9 docs: AUDIT.md 67/67 (dossier)`
- `9b4bfed feat: generated full project dossier PDF`
- `42a8382 docs: AUDIT.md 67/67 (60s guide)`
- `4864ef9 docs: 60s cut guide + resilient repo-public preflight`
- `c6a3f02 docs: AUDIT.md 67/67 (vertical cut)`
- `8da05d5 feat: 9:16 vertical 60s cut (Reels/Shorts/Stories)`
- `12a062c docs: AUDIT.md 67/67 (progressive 60s)`
- `b5ccd6a feat: 60s cut now shows the actual state progression`
- `aeabd02 docs: AUDIT.md 67/67 (exact 60s cut)`
- `b7f3057 polish: exact 60s beat timings (hook 3, quote 4, mandate 6, pay 7, attack 10, poster 6, frontier 9, verify 7, close 8)`
- `374339b docs: AUDIT.md 67/67 (60s timing)`

## 17. Appendix: environment and credits

Python 3 stdlib only · Ed25519 via OpenSSL · tesseract · ImageMagick · ffmpeg · headless Chromium. Models: Muse Spark 1.3, Muse Wonder 1.0, Muse Voice Transcribe 1.0, SAM 3.1, Muse Image 1.0, DeepSeek-chat. Human voice study uses LibriSpeech dev-clean (CC BY 4.0; no audio committed). Synthetic narration is labelled and replaceable. The demo HMAC secret is public by design; mandate signatures are real Ed25519. Full credits: `NOTICE.md`; failure list: `docs/limitations.md`; security: `SECURITY.md`.

