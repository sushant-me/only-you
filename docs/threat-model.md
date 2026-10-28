# Threat model — ONLY YOU

Scope: the demo and the design it argues for. Every claim below maps to code, a test, or a published
measurement; anything not mitigated is listed as residual.

## Assets

1. The wearer's **authority** — what the agent is allowed to do with money, doors, files and messages.
2. The **receipt ledger** — evidence of what happened, including refusals.
3. The **mandates** — scoped, expiring delegations a merchant can verify.
4. The **owner's voiceprint** and the device key.

## Trust boundaries

```
mic ──► speaker check ──┐
camera ─► scene reader ─┤
page ───► DOM labeler ──┼─► provenance router ─► model (proposes) ─► gate (decides) ─► executor ─► receipts
document ► invoice parse┘        (labels)                              (authority)
```

1. **Input → labeler**: attacker-controlled bits become labelled data. The labeler itself is fallible
   (81% recall / 14.3% FPR measured) — that is why it is not the enforcement point.
2. **Labeler → model**: labels ride into the prompt; the model sees text, not trust.
3. **Model → gate**: the model's proposal is untrusted. The gate checks provenance, constitution,
   mandate and confirmation independently of the model.
4. **Gate → executor**: only an allowed verdict reaches a tool.
5. **Receipts → display/model**: receipt text is display-sanitised and ledger context is labelled DATA,
   so a malicious payee cannot turn a receipt into an instruction.

## Adversaries and outcomes

| Adversary | Capability | Mitigation | Residual |
|---|---|---|---|
| Bystander | speaks commands near the device | only enrolled voice is a command; proximity required | — |
| Cloned voice | synthesizes owner voice | policy catches most; confirmation for irreversible actions | 20% executed in the adaptive corpus (owner present + confirms) — published |
| Malicious document | supplies payee/amount for "pay this invoice" | arguments are data; gate re-checks payee and cap | issuer-trust policy is future work |
| Poster / TV / page | injects instructions into scene or DOM | scene/web are data by channel; instruction-from-data rule | OCR/read misses affect evidence, not execution |
| Forged sensor bus | fabricates speaker score/proximity | signed sensor envelope (6/6 → 0/6) | compromised sensor still passes |
| Malicious merchant | alters mandate fields | Ed25519 signature over payee/cap/expiry; offline verify | replay across merchants not solved |
| The model itself | proposes a harmful or manipulated action | model never executes; gate denies or asks | model can waste time / cause false refusals (5%) |
| Ledger tamperer | edits receipt text | HMAC chain; editing breaks the chain | secret is demo-only (device-rooted in production) |

## Assumptions

- The device OS and the gate binary are not compromised; the voiceprint is enrolled in a trusted setup.
- The constitution is written by the owner, not by the model.
- The demo's HMAC secret is explicitly demo-only; merchant verification uses real Ed25519 keys.
- Payments are mocked (`MockWorld`); no real money moves.

## Out of scope (stated, not hidden)

- Model supply chain, weight poisoning, extraction.
- Physical/coercive attacks on the wearer; compromised OS or camera/mic firmware.
- Multi-user and shared-device authority; social recovery; mandate revocation propagation.
- Network attacks between device and merchant (TLS assumed, not built here).

## Verification map

| Claim | Where |
|---|---|
| Four-arm gate behaviour | `results/benchmark.md`, `tests/test_core.py` |
| Real-model behaviour | `results-real*/`, `docs/report.pdf` |
| Label-layer recall/FPR | `docs/report.pdf`, `tests/test_dom.py` |
| Forged sensor envelope | `results/benchmark.md` (signed/unsigned), `tests/test_sensors.py` |
| Merchant verification | `tests/test_merchant_api.py`, `tests/test_devicekey.py` |
| Ledger tamper + second-order injection | `tests/test_ledger_safety.py`, `docs/ledger-safety.md` |
| Demo server input bounds | `tests/test_web_hardening.py` |
| Known failures | `docs/limitations.md` |
