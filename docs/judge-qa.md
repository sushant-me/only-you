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

**Can one agent delegate to another?**
Yes — recursive delegation with attenuation: a sub-mandate's payees must be a subset of the parent's, its
cap cannot exceed the parent's remaining budget, its expiry cannot outlive the parent, and its sub-limits
must fit inside. Spend through the child also consumes the parent, and undo restores both.

**Can a mandate recur, like a monthly allowance?**
Yes — `period_seconds` turns the cap into a per-period allowance (e.g. ≤ 2,000/month) that resets on the
mandate's anchor. The card shows this period's spend and the reset date; a sub-mandate's period can never be
shorter than its parent's.

**Can I set per-merchant or daily limits?**
Yes — a mandate can carry signed `payee_limits` (e.g. electrician ≤ 1,000) and a `daily_limit`, both below
the cap. The gate and merchant checkout enforce them; undo restores the day's usage. Offline merchant
verification checks the static caps; the live remaining/daily budget is enforced at execution.

**Does it track spend against the mandate?**
Yes. Each executed payment consumes the mandate's budget; the UI shows spent/remaining with a progress
bar, the receipt records `remaining_after`, undo refunds the budget, and one click revokes every
delegation while keeping the receipts. A payment beyond the remaining budget is no longer covered by the
mandate — it falls back to the constitution's ask/confirm path.

**How does an actual merchant checkout work?**
`/merchant-page` (and `/api/checkout`) runs the two steps in order: the merchant verifies the presented
mandate — principal signature, scope, payee, cap, remaining budget — and only then does the agent pay
through the gate. The merchant gets the rule that authorised it, the remaining budget and a link to the
receipt's verification page.

**Can a merchant check a single receipt?**
Yes — every receipt has a `/verify/<id>` page (and `/api/receipt/<id>` JSON): action, decision, rule,
reason, signature validity, chain position, mandate spend. Fields are escaped because receipt text is
attacker-influenced. For bulk evidence, the signed audit export below verifies offline.

**Can I take the evidence away and verify it myself?**
Yes — `GET /api/export` (or **export audit** in the UI) returns a single JSON bundle: receipts with their
HMAC chain, mandates with Ed25519 signatures, the device public key, chain head and instructions.
`python3 tools/verify_audit.py audit.json` re-checks everything offline and fails if one byte is changed.

**Does it plug into a SIEM?**
Yes — policy changes, mandate revocations and rejected checkouts raise structured alerts, exposed in the UI
and in `GET /api/state`. Set `ONLYYOU_WEBHOOK_URL` and each alert is POSTed as JSON to your webhook/SIEM
(delivery is queued with retries and a delivery log, and never blocks the action).

**Can I version and deploy the policy?**
Yes — `GET /api/policy/export` is a signed snapshot (rule states + device public key); import verifies the
signature for this device, refuses unknown rules, receipts the import (`R7-policy-import`) and alerts. The
signature is device-bound in this demo: production would trust an owner/organisation key so one policy can
be rolled out to many devices.

**Are policy changes auditable?**
Yes — every enable/disable appends a signed `R7-policy-change` receipt (rule id, new state, source) to the
same hash chain, and it appears in the audit export and receipt verification pages. Changing the rules is
an auditable act, not a silent config edit.

**Can I change the policy itself?**
Yes — the constitution is editable at runtime (enable/disable any rule from the UI, `POST /api/policy`).
Pair it with the dry run: disable `R1-payee-not-contact` and the same payment proposal moves from DENY to
ASK before anything executes. `reset` restores the defaults.

**Can I test a policy change before it ships?**
Yes — the demo has a **Policy dry run** panel (and `/api/simulate`): it resolves a proposed action through
provenance, constitution and mandates and returns the decision, rule, reason and remaining budget without
executing anything or writing a receipt.

**Is the HMAC ledger secret in the repo a weakness?**
It is a demo secret, stated as such. Receipts are tamper-evident and chained; production would root the
key in the device secure element. The merchant path already uses real Ed25519 public-key verification.

**Is the voice check real?**
It is local MFCC speaker matching in the browser, not anti-spoofing. We publish a sensitivity table and
say a cloned voice passes; the gate then relies on confirmation for irreversible actions. Spoken commands
in the demo are transcribed by Muse Wonder (`/api/voice/transcribe`); transcription is not verification —
the transcript still goes through the same voice check and gate.

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
`make judge` (157 tests + live-server smoke + audit) then `make web` →
`http://127.0.0.1:8000/?script=full&fakecam=1`. Fresh clone verified; no key needed for the simulated
demo, `.env` for the real model.

**Why would Meta care?**
Capability and authority are separate problems. This lets agents be given real credentials, doors and
wallets because the blast radius is bounded by the owner's authority rather than the model's judgement.
Hiring memo: `docs/for-meta.md`.
