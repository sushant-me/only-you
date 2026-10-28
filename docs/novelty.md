# Novelty — what is new here, and what is not

Honest version first: **no single primitive is new.** Provenance labels, policy engines, signed
capabilities, hash-chained logs and taint tracking all exist. The contribution is the **product-shaped
combination** — an enforcement surface that sits outside the model, plus a measured failure map and
receipts for refusals — and the fact that it runs on Meta's own models today.

## Prior work and the gap

| Prior work | What it does | What it leaves open | What ONLY YOU adds |
|---|---|---|---|
| **WebMCP `untrustedContentHint`** (Meta) | flags untrusted tool content for the model | docs say it is "not an enforced security boundary" — it is advice to the model | turns provenance into an **enforced** precondition: data can never be the source of an executed action |
| **Prompt-injection filters / guardrails** | classify or sanitize input | asks the model to win; one wording change and it fails | does not ask the model to be robust — the gate decides what is *eligible* to be an instruction |
| **CaMeL** (DeepMind, 2025) | dual-LLM + capability/taint policies for tool calls | research harness; no owner-authored constitution, signed delegation, merchant-facing proof or refusal record | user constitution + **signed scoped expiring mandates** + offline merchant verification + receipts for actions *and refusals* + spend budget |
| **Prismata** (mask-based defense) | masks dangerous content before the model sees it | masks still need a trust decision; masking is not authority | we measure the difference: provenance-only still pays **50%** of confused-deputy attacks; the full gate pays **0%** |
| **Devil in the Lens** (camera injection) | demonstrates wearable prompt injection | attack only | enforcement + evidence path for the same class, with a measured corpus |
| **Agentic-commerce token schemes** | network-issued agent payment tokens | closed ecosystem, issuer-specific, not merchant-verifiable from first principles | open Ed25519 mandate any merchant can verify offline with a public key, with cap, budget, expiry, revocation and a receipt |
| **Hash-chained audit logs** | tamper evidence | evidence is not authority | the same ledger is what the model sees (labelled DATA), so memory cannot become the next instruction |

## The claims that are actually defensible

1. **The model never executes.** Every action is a proposal; the gate checks provenance, constitution,
   mandate budget and confirmation independently of the model.
2. **The failure map is measured, not asserted.** Four-arm benchmark (A/B/C/D), three real Muse Spark
   runs, label-layer recall/FPR with confidence intervals, forged-sensor 6/6→0/6, adaptive 20% — all
   committed, including what fails.
3. **Refusals are first-class.** Every refusal is signed and chained, so the agent's memory of what it
   declined is evidence, not silence.
4. **Delegation is commerce-shaped.** Signed scope + payee allow-list + cap + live budget + expiry +
   revocation, and a merchant verifies it offline with only the public key.
5. **Evidence leaves the system.** Signed audit export + standalone verifier + per-receipt verify pages,
   so a third party checks the record without trusting the server.

## What we deliberately do not claim

- Not the first provenance system; not the first policy gate; not a trained anti-spoofing model.
- Not a production TEE or secure-element implementation — the demo's HMAC secret is explicitly demo-only.
- SAM 3.1 masks and Muse voice transcription are not integrated (documented in `limitations.md`).

The honest positioning: **this is the enforcement and proof surface a wearable agent needs, built and
measured on Meta's stack, with the failures published alongside the wins.**
