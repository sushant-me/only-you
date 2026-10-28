> **HOLD — do not submit until Sushant explicitly says "finalize".** Everything below is staged and
> verified; the form is only pasted after his go-ahead.

# Submission — final copy-paste sheet

Deadline **4 Nov 2026, 9:00 PM ET = 5 Nov 2026, 7:45 AM NPT**. Video: upload unlisted, then paste the
YouTube URL into the one `<...>` below. Everything else is final.

## Project

- **Name:** ONLY YOU
- **One-line:** A wearable agent that knows who is allowed to command it — and can prove what it did.
- **Track:** Indie developer
- **Theme:** Build for Your World
- **Bonus categories:** Best Agentic Use-Case · Most Viral Project
  (Open Weights is **not** claimed: no open-weights deployment was run. The `muse-spark-1.3-contributor`
  build run is extra real-model evidence, not an open-weights submission.)

## Short description (≈60 words)

ONLY YOU is a provenance-gated authority layer for wearable agents. Before a token reaches the model,
every input is labelled: only the enrolled owner's voice is a command; scene text, page text and
documents are data. A user-written constitution and signed, expiring mandates gate irreversible actions,
and every action and every refusal emits a signed receipt.

## Long description (≈230 words)

Meta's WebMCP documentation for Ray-Ban Display tells developers that `untrustedContentHint` is "not an
enforced security boundary," and the assistant still cannot tell the wearer's voice from a stranger's.
Once an agent has a camera, a microphone and a wallet, a TV ad, a poster, a webpage or an invoice can
issue commands.

ONLY YOU fixes the channel instead of asking the model to be robust. Before the model sees a token, every
input is labelled by provenance: on-device speaker verification, scene reading with Muse Wonder, DOM
origin, document trust. A deterministic constitution and signed, scoped, expiring mandates gate
irreversible actions; every action and every refusal emits an HMAC hash-chained receipt with the rule, the
evidence and an undo. Mandates are signed with an Ed25519 device key, so a merchant can verify the owner's
delegation offline with only the public key.

The demo is a success, not a block: the owner delegates one payee and a cap, the agent pays an invoice
without interrupting, and a look-alike invoice with the same spoken command is refused because its payee
came from a document. A poster, a TV ad and hidden page text are read but never obeyed.

We publish the numbers that can be wrong: two real Muse Spark runs (including one where alignment alone
holds), the confused-deputy corpus where the undefended model pays 25% of the time and the full gate pays
0%, the label layer's recall and false positives, and the adaptive attacks that still get through.

## How it uses Meta AI products

| Product | Use | Evidence |
|---|---|---|
| **Muse Spark 1.3** | proposes every action; the gate re-validates; real runs at temperature 0 | `results-real/`, `results-real-doc/` |
| **Muse Wonder 1.0** | reads the camera frame into text + boxes (`/api/frame`); transcribes spoken commands (`/api/voice/transcribe`) | `results/scene-muse.json` (15/15, 0.0% CER) |
| **Muse Image 1.0** | generates the demo's poster, TV frame, invoice, article and hero | `src/onlyyou/web/fakecam-*.jpg`, `docs/img/hero.jpg` |
| Muse Spark contributor build | third real run on the same corpus (A 50% → D 0%) | `results-real-doc-contributor/` |

Not integrated (stated honestly): SAM 3.1 masks (the API exposes the model but not a usable mask output
format); Muse voice transcription (model listed, endpoint returns `model_not_found` for this key).
Both are in the roadmap in `for-meta.md`, not claimed as shipped.

## Links

- Repo: https://github.com/sushant-me/only-you
- Live page: https://sushant-me.github.io/only-you/
- 3-minute demo: **<YouTube unlisted URL>** (file: `docs/demo-3min.mp4`, 2:55, captioned)
- Report: https://github.com/sushant-me/only-you/blob/main/docs/report.pdf
- Real runs: `results-real/`, `results-real-doc/`, `results-real-doc-contributor/`
- Hiring memo: https://github.com/sushant-me/only-you/blob/main/docs/for-meta.md
- WebMCP note: https://github.com/sushant-me/only-you/blob/main/docs/webmcp-note.md
- Team: Sushant Poudel (solo)

## Built during the event

`BUILD_LOG.md` records it. One scaffold commit is labelled pre-event (provenance labels, gate,
constitution, mandates, receipts, benchmark harness). During the event: real Muse Spark loop + prompt
repair, Ed25519 device-key mandates with offline merchant verification, agentic task runner, Muse Wonder
scene reader, tesseract OCR fallback, receipt display sanitising and DATA-labelled ledger context, real
model benchmarks, Muse Image assets, the demo UI, captioned video package, CI, audit and report.

## Pre-submit check

- [ ] Repo opens logged out: https://github.com/sushant-me/only-you
- [ ] Live page returns 200 and plays the video
- [ ] YouTube link pasted above; video unlisted, ≤ 3:00, plays logged out
- [ ] `make judge` green in a fresh clone (145 tests, audit green)
- [ ] No secret in the repo (`git ls-files | grep -c env` → only `.env.example`)
- [ ] Screenshot the confirmation page and save the submission URL
