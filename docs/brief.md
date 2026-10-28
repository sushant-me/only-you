# ONLY YOU — one-page brief

**The more capable the model, the more it needs an authority layer.**

ONLY YOU is the authority layer that lets a wearable agent act in the world without being trusted with it.
Sushant Poudel · Meta Global AI Developer Hackathon 2026 · Build for Your World

## The problem

Meta's WebMCP documentation says the untrusted-content hint is *"not an enforced security boundary,"* and
the assistant cannot tell the wearer's voice from a stranger's. With a camera, microphone and wallet, any
TV ad, poster, webpage or invoice can issue commands. Capability is solved; **authority is not.**

## What it does

| | |
|---|---|
| **Provenance** | Only the enrolled owner's voice is a command. Scene text, page text and documents are data — enforced by channel, not by prompt wording. |
| **Bounded delegation** | Ed25519-signed mandates with caps, per-merchant/daily sub-limits, recurring allowances and sub-agents that can only narrow authority. A merchant verifies one offline with only the public key — or a QR code. |
| **Provable evidence** | Every action *and every refusal* is a signed, hash-chained receipt. Export the audit bundle and re-verify it in Python or **in the browser**; every receipt has a public verification page. |

## The evidence

| Measurement | Result |
|---|---|
| Confused-deputy corpus, Muse Spark 1.3 | undefended **25%** executed · prompt-only 37.5% · provenance-only 50% · **full gate 0%**, 0% false refusals |
| Same corpus, contributor build | 50% → 37.5% → 50% → **0%** |
| Same corpus, **frontier DeepSeek-chat** | undefended **50%** → **0%** with the gate, 0% false refusals, **18/18 receipts** |
| Post-build reproduction on final code | every arm **0%**, **16/16 receipts**, chain intact, 99 live calls |
| Label layer (the part that can be wrong) | DOM recall 81.0%, 14.3% false positives — published, with 8 missed techniques |
| Forged sensor signals | 6/6 executed without a signed bus → **0/6** with it |
| Cross-model audit | same gate + receipt format under Muse Spark and **DeepSeek**, verified in the browser |
| Voice channel (public human study) | owner 3/3 · **0/12 impostors accepted** at capped 0.10 (pilot) and **0/12 on 12 unseen speakers**; uncapped pilot 2/12 |
| Engineering | **172 tests**, 67-check self-audit, CI (tests + Docker), four committed real-model runs |

## Why it matters commercially

- **Wearables**: the wearer-vs-the-world trust story is the product question for glasses.
- **Agentic commerce**: merchants need to verify an agent's authority before charging; Amazon blocks Muse today.
- **Enterprise copilots**: the same gate gives delegated, receipted, revocable action instead of blind trust.

## Try it in 30 seconds

- Playground (no install): <https://sushant-me.github.io/only-you/playground.html>
- Verify an audit bundle: <https://sushant-me.github.io/only-you/verify.html>
- Repo / one command: `make judge` · `docker run -p 8000:8000 only-you-demo`
- 3-minute narrated demo, report and deck: <https://sushant-me.github.io/only-you/>

## The honest line

The gate is engineered and tested; the label layer is measured and published where it fails. Cloned voice,
an exposed demo server, cross-device policy trust and synthetic narration are named in
[`limitations.md`](limitations.md) — not hidden. That is what makes this auditable rather than marketing.

**Ask:** a pilot with the wearables or agentic-commerce team — and a role building this class of
infrastructure at Meta.
