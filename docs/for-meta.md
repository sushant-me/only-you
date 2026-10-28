# For Meta

**ONLY YOU is the authorization layer that lets a frontier agent act in the world without being trusted with it.**

## The gap this closes

A frontier model is now capable enough to pay, book, message, unlock and delete. The only thing standing
between that capability and a real account is the model's willingness to refuse — prompt-level alignment,
not an authorization system. The model's own documentation says the untrusted-content hint is "not an
enforced security boundary." Our real-model runs show the size of the hole: on a confused-deputy corpus,
Muse Spark executed **25% of attacks undefended, 37.5% with prompt hardening, 50% with provenance labels
only**, because the owner really did ask to pay and the document supplied the payee.

## What this makes possible

Capability and authority are different problems. ONLY YOU separates them:

1. **Provenance** — only the enrolled voice is a command channel; scene, page and document text are data
   by channel, not by prompt wording.
2. **Proposal, not execution** — the model proposes; a deterministic gate decides. The model cannot
   execute anything it is not authorised to, even when it is fully convinced.
3. **Delegation with bounds** — the owner grants an Ed25519-signed, scoped, expiring mandate with caps,
   per-merchant and daily sub-limits, recurring allowances, and sub-agents that can only narrow authority.
   A merchant verifies it offline with only the public key — or a QR code at the counter.
4. **Evidence, not trust** — every action *and every refusal* becomes an HMAC-chained receipt with rule,
   source and argument provenance. The audit bundle re-verifies offline (`tools/verify_audit.py`) or in a
   browser with WebCrypto, and every receipt has a public verification page. The ledger enters the model's
   context as data, never as instructions.
5. **Operations** — receipted policy changes with a review diff, signed SIEM alerts with retries, scheduled
   standing instructions that re-check a live mandate at run time, and a ledger that filters and exports to
   CSV for audit triage.

Result: you can give an agent real credentials, a real door, a real wallet — because the blast radius is
bounded by the owner's authority, not by the model's judgement. That is what turns a demo agent into a
product people will let act for them.

**Also shipped:** Muse Voice Transcribe transcribes spoken commands in the demo (`/api/voice/transcribe`), so the
voice path is a Meta model end-to-end instead of typed text. It is transcription, not speaker
verification — the MFCC check still decides whose voice it is. Merchant checkout, the browser playground,
the audit verifier and a Docker image make the whole thing tryable in 30 seconds.

## Evidence (real Muse Spark runs, temperature 0)

| Corpus | Undefended | Prompt-only | Provenance-only | **Full ONLY YOU** | False refusals |
|---|---|---|---|---|---|
| Confused deputy, Muse Spark 1.3 (8 / 12) | 25% | 37.5% | 50% | **0%** | **0%** |
| Confused deputy, Muse Spark contributor build | 50% | 37.5% | 50% | **0%** | **0%** |
| General injection (20 / 20) | 0%* | 0%* | 0%* | **0%** | 0–5% |

\* Muse Spark's own alignment refuses obvious injections even undefended; the authority layer earns its
place on the attacks alignment is trained to be helpful about. 195 + 115 real calls, 36/36 and 18/18
receipts verified; constitution rules 0.001 ms p50; full dry-run path 4.3 ms; local HTTP command 12.8 ms; OCR 156 ms; end-to-end p50 6.8–11.9 s is dominated by the model call (results/latency.json).
Receipts and raw results are committed: `results-real/`, `results-real-doc/`.

## What I would build next with Meta

1. **WebMCP authority propagation** — extend `untrustedContentHint` from a hint into a signed provenance
   label on every tool result, so the gate can enforce where a tool call's arguments came from.
2. **Scene understanding with SAM 3.1** — replace approximate OCR boxes with masks, so "authority
   regions" in the visual field are precise (text vs face vs screen).
3. **Device-rooted mandates** — device key in the secure element, attestation bound to the mandate, so a
   merchant can verify not just the owner's signature but the device state that produced it.
4. **An authority-failure eval across Muse models** — the confused-deputy corpus, the adaptive corpus and
   forged sensor signals as a reusable benchmark for "can this model be trusted to act?"
5. **Muse Wonder in the loop** — 1M-context scene + conversation summarisation with the receipt ledger
   entering as labelled data, which is the only way an always-on wearable can remember without being
   reinfected by its own memory.

## Why me

I built this in the hackathon window, alone: 172 tests, a self-audit, CI (tests + Docker), three real-model runs,
and an honest failure list — including the cases where the layer does not help. I want to keep building
this at Meta, on the team that ships agents people can actually delegate to.

Repo: <https://github.com/sushant-me/only-you> · Page: <https://sushant-me.github.io/only-you/>
