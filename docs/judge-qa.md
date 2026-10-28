# Judge Q&A — short, honest answers

**What is this, in one sentence?**
A provenance-gated authority layer: only the enrolled owner's voice is a command; scene/page/document
text is data; irreversible actions need a signed mandate; every action and refusal becomes a receipt.

**Is this just another prompt-injection filter?**
No. It runs before and outside the model: a deterministic gate decides what the model is allowed to
execute, whatever the model was persuaded to propose. The model is never the enforcement point.

**Does it work with the real model?**
Yes — three committed runs on the Meta Model API at temperature 0. On the confused-deputy corpus Muse
Spark executed 25% of attacks undefended, 37.5% prompt-only, 50% provenance-only, and **0% with the
full gate** (contributor build: 50% → 0%), with 0% false refusals and 18/18 receipts verified.
`results-real*/`.

**Why does an undefended model pay a look-alike invoice 25% of the time?**
Because the owner really did ask to pay an invoice; the document supplied the payee. Alignment is
trained to be helpful, not to check authority. That is the gap this layer closes.

**Is the HMAC ledger secret in the repo a weakness?**
It is a demo secret, stated as such. Receipts are tamper-evident and chained; production would root the
key in the device secure element. The merchant path already uses real Ed25519 public-key verification.

**Is the voice check real?**
It is local MFCC speaker matching in the browser, not anti-spoofing. We publish a sensitivity table and
say a cloned voice passes; the gate then relies on confirmation for irreversible actions.

**What about SAM 3.1?**
The API exposes `sam-3.1` on `/v1/responses` but my text-prompt requests returned an empty output with
`images_processed: 1`; I could not find a usable mask format. It is on the roadmap, not claimed as
integrated. Scene reading uses Muse Wonder with tesseract fallback.

**What fails?**
Published in `docs/limitations.md`: cloned voice + owner confirmation (20% execution in the adaptive
corpus), 1/8 evidence coverage on paraphrased payloads, label-layer recall 81% / FPR 14.3%, small
synthetic samples. The gate holds; the perception and evidence layers are the weak parts.

**Does it slow the agent down?**
The in-process gate is ≈0.1 ms. End-to-end p50 is dominated by the model call: 6.8 s general, 10.7 s
document, 11.9 s contributor build. Perception latency is not claimed.

**Can a third party verify what happened?**
Mandates are Ed25519-signed; a merchant verifies signature, payee, cap and expiry offline with the public
key (`/api/merchant-verify`, demo "verify at merchant" button). Receipts are HMAC-chained and displayed
sanitised; the ledger enters the model's context as DATA, never as instructions.

**How do I run it?**
`make judge` (105 tests + live-server smoke + audit) then `make web` →
`http://127.0.0.1:8000/?script=full&fakecam=1`. Fresh clone verified; no key needed for the simulated
demo, `.env` for the real model.

**Why would Meta care?**
Capability and authority are separate problems. This lets agents be given real credentials, doors and
wallets because the blast radius is bounded by the owner's authority rather than the model's judgement.
Hiring memo: `docs/for-meta.md`.
