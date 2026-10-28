# Press / share kit

Everything here is free to use with the project name **ONLY YOU** and a link to
<https://github.com/sushant-me/only-you>. Images are generated for this project (Muse Image + HTML
renders); the repo is MIT, the screenshots are yours to reuse.

## Boilerplate

**One line.** A provenance-gated authority layer for wearable agents: only the owner's enrolled voice is a
command, everything else is data, and every action and refusal leaves a verifiable receipt.

**50 words.** ONLY YOU is an authority layer for wearable agents. Before a token reaches the model, every
input is labelled by provenance — only the enrolled voice can command; scene, page and document text are
data. A signed mandate bounds what the agent may do, and every action and refusal emits a hash-chained
receipt that anyone can verify offline.

**150 words.** Meta's own WebMCP documentation says the untrusted-content hint is "not an enforced security
boundary," and an assistant still cannot tell the wearer's voice from a stranger's. With a camera,
microphone and wallet, a TV ad, poster, webpage or invoice can reach the same context window as the wearer.
ONLY YOU closes that gap outside the model: inputs are labelled by channel, a deterministic constitution
and Ed25519-signed, scoped, expiring mandates gate irreversible actions (caps, per-merchant/daily
sub-limits, recurring allowances, sub-agents that can only narrow authority), and every action *and every
refusal* becomes a signed, hash-chained receipt. Merchants verify a mandate offline with the public key;
anyone can re-verify the audit export in Python or in the browser. On a confused-deputy corpus, Muse Spark
executed 25% of attacks undefended — and 0% with the full gate.

## Headlines

1. **Your glasses can hear the world. Who do they obey?**
2. **The layer that decides who your agent answers to.**
3. **25% → 0%: what an authority layer does that alignment doesn't.**
4. **Don't trust the dashboard. Verify the receipt yourself.**

## Stats that are committed

- Confused-deputy corpus, Muse Spark 1.3: **25% undefended → 0% full gate**, 0% false refusals
- Second model build: 50% → 37.5% → 50% → **0%**
- Final-code reproduction: every arm **0%**, 16/16 receipts, chain intact
- Forged sensor signals: **6/6 → 0/6** with a signed bus
- **172 tests**, 67-check self-audit, CI (tests + Docker)
- Honest misses: label layer 81.0% recall / 14.3% FPR; adaptive attacks still get **20%** through

## Images (1200×675)

| File | Use | Alt text |
|---|---|---|
| [`img/x-stat.png`](img/x-stat.png) | hook post / article | Dark card: "25% → 0%", undefended vs full ONLY YOU, Muse Spark confused-deputy corpus |
| [`img/x-quote.png`](img/x-quote.png) | quote post | Dark card quoting Meta's WebMCP docs: untrustedContentHint is "not an enforced security boundary" |
| [`img/x-try.png`](img/x-try.png) | replies / stories | Dark card: "Try the gate yourself", three bullets, playground URL |
| [`img/hero.jpg`](img/hero.jpg) | article header | Smart glasses with a red rim light |
| [`demo-x-vertical.mp4`](demo-x-vertical.mp4) | X / Reels / TikTok | 45 s vertical cut |

## Links

- Repo: <https://github.com/sushant-me/only-you>
- Page: <https://sushant-me.github.io/only-you/>
- Playground: <https://sushant-me.github.io/only-you/playground.html>
- Verify a bundle: <https://sushant-me.github.io/only-you/verify.html>
- One-page brief: <https://github.com/sushant-me/only-you/blob/main/docs/brief.pdf>

## Contact

Sushant Poudel — open an issue or comment on the repo; I answer technical questions with the committed
numbers. Please do not quote the demo as production-secure: `docs/limitations.md` lists what is
demo-only.
