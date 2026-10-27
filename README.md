# ONLY YOU

**Your glasses can hear the world. Who do they obey?**

A provenance-gated authority layer for wearable agents — built with **Muse Spark** and **SAM 3.1**
through the Meta Model API during the Meta Global AI Developer Hackathon 2026.

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
   - on-device speaker verification — only the enrolled owner's voice is a command channel;
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
   enforcement event is never confused with a UI attribution.

4. **Merchant-verifiable mandates.** Mandates are signed with an **Ed25519 device key**, so a merchant
   can verify the owner's delegation offline with only the public key — no shared secret, no call to
   the platform. `python3 tools/mandate_demo.py` issues one and verifies it both ways.

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

## Demo

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
| Scene text (render → OCR) | detection 94.3%, mean CER 9.4%; 0/35 executed |
| Signed sensor envelope | 6/6 executed without → 0/6 with |
| Ed25519 merchant verifier | valid mandate VERIFIED offline; tampered / over-cap / expired REJECTED |

The zero is a harness property, not a security claim. The falsifiable numbers are the label layer and
the adaptive corpus. Known failures are listed in [`docs/limitations.md`](docs/limitations.md).

## Quickstart

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
make gen test          # corpus + 89 tests
make bench             # writes results/benchmark.md
make demo              # end-to-end story
make web               # UI at http://127.0.0.1:8000
```

Optional extras for OCR/scene evaluation: `pip install -r requirements-optional.txt` and system
`tesseract`, `imagemagick`.

## Repo layout

```
src/onlyyou/     provenance, actions, policy, mandates, receipts, sensors, scene, agent, web UI
tests/           89 tests
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
