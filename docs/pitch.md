# ONLY YOU

**A wearable agent that knows who is allowed to command it — and can prove what it did.**

Sushant Poudel · Meta Global AI Developer Hackathon 2026

## Your glasses can hear the world. The question is who they obey.

> "Set `untrustedContentHint` honestly, since **it's not an enforced security boundary**."
> — Meta Wearables Developers, WebMCP agent tools

> "Your tool's result text goes into the assistant's context, so returning unmarked untrusted content is how a prompt injection reaches the model."

## The gap

- The agent cannot tell an **instruction** from **content**.
- It cannot tell its **owner** from a **bystander**.
- Once it has a camera, a mic and a wallet, the world can command it.

A TV ad, a poster, a hidden webpage, an invoice — all of them reach the same context window.

## The three primitives

- **Identity** — only the enrolled owner's voice is a command channel. Everything else is data.
- **Mandates** — signed, scoped, expiring delegation: "pay the electrician up to 5,000 until tomorrow." A merchant can verify it.
- **Receipts** — every action *and every refusal*: evidence, rule, hash chain, undo.

The model is never trusted with authority. It proposes; the gate decides.

## The demo

![ONLY YOU demo](img/ui-final.png)

1. Grant the mandate — signed, capped, expiring.
2. Pay the invoice — no prompt, receipt cites the mandate.
3. A look-alike invoice with the *same spoken command* — blocked, payee came from a document.
4. TV ad, poster, hidden page text — blocked with the source highlighted.
5. "What did you do today?" — answered from the ledger.

## What I measured

| Measurement | Result |
|---|---|
| Four-arm harness (conditional on correct labels) | A 100% · B 47.5% · C 10% · D 0% executed |
| DOM labeler — inline-style regex | recall 81.0% [66.7–90.0], FPR 14.3% [6.3–29.4] |
| Same cases — browser computed styles | 42/42, 0/35 (upper bound) |
| Adaptive corpus — forged signals | label error 80%, executed 20% (3/15) |
| Evidence coverage | 1/8 paraphrased payloads produced a receipt |
| Scene text — render → OCR → gate | detection 94.3%, 0/35 executed, 24/35 receipts |

The zero is **conditional on correct labels**. The falsifiable numbers are the label layer and the adaptive corpus.

## What breaks it

- **Cloned voice** at 0.91: 12/12 label errors, 3/15 executions.
- **Forged sensor dict**: mitigated — signed sensor bus, 6/6 → 0/6 (measured).
- **Rotated scene text**: 60% detection — enforcement holds, evidence degrades.
- **Merchant verification**: design sketch; needs a device public key.
- **Biometric consent**: voiceprints are special-category data; no consent flow yet.

## Why it matters

- **Glasses** become trustworthy only if the agent distinguishes the wearer from the world.
- **Agentic commerce** needs merchants to verify that a purchase was authorised — Amazon already blocks Muse because it cannot.

The narrow claim: *do not make the model robust to injection; make the channel untrusted by default.*

## With ten engineers

1. Ship the WebMCP provenance envelope — an `authority` field the assistant enforces.
2. Voice + DOM provenance in the Muse client, signed sensor bus.
3. Mandates on device keys + offline merchant verifier.
4. Scene provenance; publish the benchmark and corpus.

Repo, benchmark, raw logs, and the failure list: [link]
