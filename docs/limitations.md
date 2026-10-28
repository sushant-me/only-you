# What breaks this — named attacks, severity, status

A security page that only lists successes is marketing. This is the other page: eight attacks against
ONLY YOU, what they achieve, and whether this build fixes them. Status values: **fixed**, **mitigated**
(detection/reporting, not prevention), **open**.

| # | Attack | What it achieves | Evidence | Severity | Status |
|---|---|---|---|---|---|
| 1 | **Cloned voice** at speaker score 0.91 + spoofed proximity | Router labels the attacker's utterance as the owner; the model proposes the action | Adaptive corpus: 12/12 label errors; 3/15 executions (cases where the owner then confirmed) | Critical | **Open** — biometric FAR is unmeasured; needs liveness challenge + on-body/proximity attestation |
| 2 | **Prefilled textarea / page claims "user typed"** | Would make web text a command channel | Adaptive corpus: 0/3 label errors, 0/3 executed after the fix | High | **Fixed** — web text is never command-capable; owner commands come from the mic only |
| 3 | **DOM hiding techniques the regex lacks** (`clip-path`, `clip`, `transform:scale(0)`, zero-height, `rgba(255,255,255,1)`, `position:fixed` off-screen, `visibility:collapse`, `<input type=hidden>`, class-only) | Hidden instructions pass the inline-style labeler | 81.0% recall on 42 hidden cases; 8 techniques missed | High | **Mitigated in the production candidate** — a Chromium computed-style labeler scores 42/42 with 0/35 false positives on the same cases (upper bound); the regex remains the offline fallback |
| 4 | **White-on-dark UI text** | False positive: legitimate text flagged as hidden | 14.3% FPR on 35 benign snippets | Low | **Open** — heuristic cannot see the background |
| 5 | **Paraphrased instruction** with no trigger verb ("kindly remit…") | Enforcement holds (nothing executes) but **no receipt** is produced | 0 executed, 1/8 receipts | Medium | **Open** — the display/evidence layer is regex-limited; the gate is not |
| 6 | **Second-order injection through the ledger** (defence implemented, see `docs/ledger-safety.md`) ("what did you do today?" with attacker text in a receipt) | With a model-generated answer, attacker text re-enters the prompt as trusted context | Not exercised in this build: `ask()` is a deterministic template over receipts | High | **Open by design** — when the 1M-context summariser is wired, ledger entries must be passed with provenance labels, not as instructions |
| 7 | **Forged sensor dict** (`signals` is an unauthenticated JSON blob) | Any component that can write `signals` can claim owner voice or hidden text | Ablation: 6 fabricated-signal attacks execute 6/6 without an envelope, 0/6 with a signed sensor bus | Critical | **Fixed for the cheap forgery** — strict router rejects unsigned signals (6 → 0); a compromised sensor or cloned voice still passes |
| 8 | **Device-key compromise / mandate forgery** | Forge a mandate and spend the owner's money | HMAC secret in the demo (`DEMO_SECRET`) | Critical | **Out of scope, named** — hardware key (Secure Enclave/TPM) and rotation are product work |
| 9 | **Occluded / synthetic-only scene text** | Occlusion degrades the read; the corpus is rendered, not camera-captured | 35 synthetic signs, raw + deskew OCR: detection **100%**, mean CER **1.7%** (occluded 9.8%); pipeline 0/35 executed, **27/35 receipts** (77.1%) | Medium | **Open (synthetic only)** — enforcement holds (scene is data); camera capture and field conditions are unmeasured |
| 10 | **Cumulative mandate spend** | Old code checked each payment against the cap, not the sum | Now: `Mandate.consumed` + `remaining()`; second payment over budget is refused | High | **Fixed** (tested) |
| 11 | **Scheduled standing instructions** | A stored instruction could outlive the authority it was created under | At every run the live mandate is re-checked; revoked/expired/over-budget runs are blocked and alerted (`R8-scheduled` receipts only on success) | High | **Fixed in the demo path** — no cron daemon ships; "run now" drives the same code the scheduler would |
| 12 | **Sub-mandate widening** | An agent could grant itself broader authority | `issue_sub` rejects payees outside the parent, caps above the parent's remaining budget, longer expiry, shorter recurring periods; spending consumes every ancestor | High | **Fixed** (tests) |
| 13 | **Policy import injection** | A crafted bundle could change the constitution | Import verifies a device-bound Ed25519 signature, rejects unknown rules, shows a diff before applying, and receipts the change | High | **Fixed for this device** — cross-device rollout needs an organisation/owner key, not built |
| 14 | **Webhook spoofing** | A random POST could look like an ONLY YOU alert | Deliveries carry `X-OnlyYou-Signature` (HMAC over the body) and `X-OnlyYou-Event`; retries and a delivery log | Medium | **Fixed in demo** — production needs mTLS + durable queueing; demo secret is public |
| 15 | **Demo server exposed to the internet** | No auth, no TLS, single in-memory user, mock payments | Docker exposes port 8000 with no authentication | High | **Out of scope, named** — run locally or behind an authenticated proxy; never expose the demo as-is |
| 16 | **Synthetic narration** | The shipped voice track is neural TTS, not the author | `docs/demo-3min.mp4` audio; script in `docs/narration-script.md` | Low | **Open by design** — replaceable with a human recording via `make voice VOICE=...`; disclosed in the docs |

## What this page implies for the pitch

- The **gate** (provenance routing + policy + mandates + receipts) is the part that is engineered and
  tested; the **label layer** is the part that is assumed, and the adaptive corpus measures the cost of
  the assumption.
- The honest headline is: *"we removed the instruction path for untrusted channels, measured the layer
  that decides what 'untrusted' means, and published where it fails."*
- The three fixes worth demoing are #2 (web is never a command), #9 (cumulative cap), and the
  `proposed_by` tag that distinguishes a model-proposed block from a display-only attribution.

## Attack 6 in more detail (the one a reviewer will ask about)

The receipts are evidence, and evidence is attacker-influenced text. Today `ask()` is a deterministic
template: it *quotes* receipt fields, it does not feed them to a model as instructions. The moment the
1M-context summariser is wired in, the ledger becomes a prompt. The rule must be the same as everywhere
else: **ledger entries enter the summariser as data with provenance labels, and the summariser's output
is not an action.** That is a design constraint, not a solved problem — and it is the first thing I
would test with a real model.

## Legal / consent (not a footnote)

Voiceprints are special-category biometric data: GDPR Art. 9, India's DPDP Act 2023, and Illinois BIPA
(private right of action) all apply. "Embeddings stay on-device" is a *storage* claim, not consent.
This demo enrolls only its author, keeps no audio, and films a consenting friend. A product needs an
enrollment consent flow, a retention/deletion policy, a bystander policy (the people whose voices are
scored and rejected), and a release for any footage used in the video. None of that is built here, and
the submission says so.
