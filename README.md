# ONLY YOU

**Your glasses can hear the world. Who do they obey?**

A provenance-gated authority layer for wearable agents — designed for **Muse Spark** and **SAM 3.1**
through the Meta Model API, built during the Meta Global AI Developer Hackathon 2026.

**Repository:** <https://github.com/sushant-me/only-you> · **Live page:** <https://sushant-me.github.io/only-you/>

![ONLY YOU](docs/img/hero.jpg)

[![tests](https://github.com/sushant-me/only-you/actions/workflows/ci.yml/badge.svg)](https://github.com/sushant-me/only-you/actions/workflows/ci.yml)

**In 30 seconds.** Only the enrolled owner's voice is a command; camera text, page text and documents
are data; irreversible actions need a signed, scoped mandate; every action *and every refusal* leaves a
verifiable receipt. The demo: the owner delegates one payment, the agent pays an invoice without
interrupting, and a look-alike invoice with the same spoken command is refused because its payee came
from a document.

- **3-minute demo (2:55, captioned):** [`docs/demo-3min.mp4`](docs/demo-3min.mp4) — upload kit in [`docs/youtube-upload.md`](docs/youtube-upload.md)
- 20-second agentic task clip: [`docs/demo-task-clip.mp4`](docs/demo-task-clip.mp4)
- 82-second silent walkthrough (fallback): [`docs/demo-fallback.mp4`](docs/demo-fallback.mp4)
- 2-page report: [`docs/report.pdf`](docs/report.pdf) · benchmark: [`results/benchmark.md`](results/benchmark.md)
- Honest failure list: [`docs/limitations.md`](docs/limitations.md)

> "Set `untrustedContentHint` honestly, since **it's not an enforced security boundary**."
> "Your tool's result text goes into the assistant's context, so returning unmarked untrusted content
> is how a prompt injection reaches the model."
> — Meta Wearables Developers, WebMCP agent tools

## The problem

A wearable agent sees through a camera, hears through a microphone, reads pages and holds a wallet.
But it can't tell an **instruction** from **content**, or its **owner** from a **bystander**. A TV ad,
a poster, a look-alike invoice or a hidden line of page text can reach the same context window as the
wearer's voice.

The missing layer isn't intelligence. It's **authority**: which inputs are instructions at all, who
may issue them, what they may authorise, and what can be proven afterwards.

## What it does

1. **Provenance before the model.** Every input is labelled before a token reaches the model:
   - a local voice check — only the enrolled owner's voice is a command channel (browser capture, MFCC on the same machine; not anti-spoofing);
   - scene-text masks + OCR — physical text is data, never a command;
   - DOM origin — page text is data;
   - document trust — invoices are arguments, not instructions.

2. **A constitution and mandates.** Deterministic rules first (`R1-payee-not-contact`,
   `R2-payment-over-limit`, …), a small evaluator only for ambiguity, ask-once for irreversible
   actions. A mandate is a signed, scoped, expiring delegation — *"pay the electrician up to 5,000
   until tomorrow"* — that the agent can act under without interrupting the wearer, and that a
   merchant can verify.

3. **Receipts.** Every action and every refusal emits an HMAC hash-chained receipt with the evidence,
   the rule applied, and an undo. Refusals are tagged `proposed_by: model | display_only`, so an
   enforcement event is never confused with a UI attribution. Receipts are **evidence, never
   instructions**: display text is sanitised and the model-facing context labels ledger entries as
   DATA ([`docs/ledger-safety.md`](docs/ledger-safety.md)).

4. **Merchant-verifiable mandates.** Mandates are signed with an **Ed25519 device key**, so a merchant
   can verify the owner's delegation offline with only the public key — no shared secret, no call to
   the platform. In the demo, each mandate has a **verify at merchant** button; the CLI
   `python3 tools/mandate_demo.py` does the same check offline.

### Voice channel

`src/onlyyou/voice.py` — enrol three clips in the browser, then verify a command. Energy gate → MFCC →
mean/std embedding → distance threshold learned from enrolment. It is a channel demonstrator, not an
anti-spoofing model: a cloned voice passes, and `docs/voice.md` says so. Synthetic validation: same
voice 0.004 vs limit 0.06 accepted; different voice 0.339 rejected; silence rejected.

### Agentic task runner

`docs/demo-task-clip.mp4` — a 20-second captioned walkthrough of the task trace.

![Agent task step trace](docs/img/task-panel.png)


`POST /api/task` runs a multi-step task against a real page: browse → extract visible and hidden text
→ decide under the mandate → execute or refuse → file a receipt → explain the result. A hidden
instruction on the page is labelled data and ignored while the visible invoice is paid. `POST
/api/frame` runs scene OCR (tesseract) on a camera frame and returns the labelled text plus mask boxes.

The model is never trusted with authority. It proposes; the gate decides.

## Built during the hackathon

One commit is labelled `scaffold: pre-event ONLY YOU prototype` (provenance routing, gate, mandates,
receipts, benchmark harness). Everything below was built on top of it during the event:

- **Ed25519 device-key mandates** + an **offline merchant verifier** (`tools/mandate_demo.py`)
- **Agentic multi-step task runner** (`/api/task`): browse → extract visible and hidden text → decide →
  act → receipt → explain, with a live step trace in the UI
- **Scene OCR** (`/api/frame`, tesseract) with mask boxes; **local voice check** (MFCC enrolment)
- **Meta Model API client** (retries, token stats, JSON repair) and a **real-model benchmark mode**
- **Integration tests** for `bench --model meta` and `--model open` against a mock endpoint
- The **videos, report, deck, submission kit and live-final runbook**

`BUILD_LOG.md` has the dated record.

### Muse Spark 1.3 — real-model runs

| Corpus | Executed | False refusals | Receipts | p50 (D) |
|---|---|---|---|---|
| General (20 attacks / 20 benign) | A/B/C/D **0%** | D 5% · C 10% · A/B 0% | 36/36 verified | 6.8 s |
| Document / confused-deputy (8 attacks / 12 benign) | A 25% · B 37.5% · C 50% · **D 0%** | 0% | 18/18 verified | 10.7 s |

On obvious injections, Muse Spark's own alignment refuses even when undefended. Where the model is
trying to be *helpful* — the owner asks to pay an invoice and the document supplies the payee — it
complies 25–50% of the time, provenance alone is worse (50%), and the full gate blocks 8/8 with zero
false refusals. Raw results: [`results-real/`](results-real/benchmark.md),
[`results-real-doc/`](results-real-doc/benchmark.md).

## What is real today

| Component | Status |
|---|---|
| Provenance routing, constitution, action gate | implemented, tested |
| Signed mandates + offline merchant verification | implemented (Ed25519), tested |
| Receipts + hash chain + undo | implemented, tested |
| Local voice check (MFCC, distance threshold) | implemented; **not anti-spoofing** — a cloned voice passes |
| Scene reading | **Muse Wonder** when a key is set (text + approximate boxes; 15/15, 0.0% CER on a synthetic sample); **tesseract** fallback offline |
| Page extraction (visible + hidden) | implemented (regex DOM classifier) |
| Agent model | **Muse Spark** when `META_API_BASE`/`META_API_KEY` are set; **simulated** otherwise, and the report stamps which mode |
| SAM 3.1 segmentation | **not integrated** — OCR boxes are the segmenter in the demo |
| Payments / doors / email | mock world, no real accounts |

## Demo

- **Pitch deck:** [`docs/pitch.pdf`](docs/pitch.pdf) — 9 slides, event-built features
- **Task clip:** [`docs/demo-task-clip.mp4`](docs/demo-task-clip.mp4) — 20 s captioned walkthrough
- **Fallback video:** [`docs/demo-fallback.mp4`](docs/demo-fallback.mp4) — 82 s silent, captioned, screen-only
- **Vertical X clip:** [`docs/demo-x-vertical.mp4`](docs/demo-x-vertical.mp4) — 45 s, 1080×1920, captioned (viral prize)

The 3-minute demo: the owner grants one mandate; the agent pays an invoice without interrupting; a
look-alike invoice with the **same spoken command** is refused because its payee came from a document;
a poster, a TV ad and hidden page text are read but never obeyed; then the agent explains its day from
the receipt ledger.

`make demo` prints the story as text. `make web` runs the UI.

## Using the Meta Model API

```bash
cp .env.example .env      # fill META_API_BASE, META_API_KEY, MUSE_MODEL
export $(grep -v '^#' .env | xargs)
make smoke                # one real call, prints status + latency
PYTHONPATH=src python3 -m onlyyou.cli bench --model meta --out results-meta
```

`--model meta` runs the full 40-attack / 100-benign benchmark against **Muse Spark**, with every
proposal re-validated by the action gate. The gate is the product; the model is replaceable.

## Measured, and honestly so

| What | Result |
|---|---|
| Four-arm harness | A 100% · B 47.5% · C 10% · D 0% executed — **conditional on correct labels** |
| DOM labeler (inline-style regex) | recall 81.0% [66.7–90.0], FPR 14.3% [6.3–29.4] |
| Browser computed-style labeler | 42/42, 0/35 false positives (upper bound) |
| Adaptive corpus (forged signals) | label error 80%, executed 20% (3/15) |
| Scene text (render → OCR, raw + deskew) | detection **100%** (35/35), mean CER **1.7%**; 0/35 executed |
| Signed sensor envelope | 6/6 executed without → 0/6 with |
| Ed25519 merchant verifier | valid mandate VERIFIED offline; tampered / over-cap / expired REJECTED |

The zero is a harness property, not a security claim. The falsifiable numbers are the label layer and
the adaptive corpus. Known failures are listed in [`docs/limitations.md`](docs/limitations.md).

## Submission

- [`docs/open-weights.md`](docs/open-weights.md) — the optional Muse Glimmer entry and how to wire it
- [`docs/outreach.md`](docs/outreach.md) — 12 contacts, message templates, follow-up rules

- [`docs/submission-checklist.md`](docs/submission-checklist.md) — publish, record, submit, bonuses
- [`docs/x-post.md`](docs/x-post.md) — the 45-second vertical clip and post variants for the viral prize
- [`docs/live-finals.md`](docs/live-finals.md) — 5-minute run of show and 15 judge questions

## CI

Every push runs the full suite, the demo and the self-audit on GitHub Actions
(`.github/workflows/ci.yml`). The badge appears once the repo is published.

## Self-audit

```bash
make audit    # 40 checks: tests, benchmark numbers, links, secrets, artifacts, durations
```

## Quickstart

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
make gen test          # corpus + 104 tests
make bench             # writes results/benchmark.md
make demo              # end-to-end story
make web               # UI at http://127.0.0.1:8000
```

Optional extras for OCR/scene evaluation: `pip install -r requirements-optional.txt` and system
`tesseract`, `imagemagick`.

## Repo layout

```
src/onlyyou/     provenance, actions, policy, mandates, receipts, sensors, scene, agent, web UI
tests/           104 tests
examples/        mandate demo
tools/           PDF builder, consistency audit, Meta API smoke test
docs/            report, pitch, limitations, WebMCP note, video script
BUILD_LOG.md     dated build log for the event window
```

## License

MIT — see [`LICENSE`](LICENSE).

---

Built during the **Meta Global AI Developer Hackathon 2026** (26 Oct – 4 Nov).
Event-period work is tracked in [`BUILD_LOG.md`](BUILD_LOG.md).
