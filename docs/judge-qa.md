# Judge Q&A — the 14 questions you will get

Answer in one breath, then show the artifact. Never argue; point at the repo.

---

**1. "Isn't this just prompt-injection defense? That's a crowded space."**

The defense literature is crowded and I cite it honestly. Devil in the Lens (2026) shows physical
injection at up to 96% ASR on wearable VLMs **and already proposes a mask-based external filter**, so
my SAM-mask step is re-derivation, not contribution. Prismata (2026) does DOM provenance at 85.5% →
0.7% and explicitly claims bounded mislabelling — the guarantee my labeler lacks. CaMeL does
provenance-carrying capabilities. All three are single-modality research prototypes.
ONLY YOU is the first **cross-channel** authority layer — voice identity, scene text, DOM, documents,
QR in one policy engine — with a **user-facing evidence surface**. And it fills a gap Meta documented
itself: `untrustedContentHint` is "not an enforced security boundary."

**2. "Why won't Meta just build this?"**

They shipped the hook and wrote the admission. What's missing is the enforcement contract and the
consumer UX. A platform team can adopt a reference implementation faster than it can design one, and
the WebMCP docs already tell developers to defend themselves. The pitch is: here is the contract, here
is the reference implementation, here is the benchmark.

**3. "What is actually novel?"**

Four things: (1) **speaker identity as an authorization channel** — not personalization, a categorical
"a stranger's voice is not a command"; (2) **cross-channel unification**; (3) **the receipt** as the
product — trust from evidence, not refusals; (4) **enforcing Meta's own hint contract** for tool
results. The ablation is the proof of the thesis: provenance alone still pays an attacker's invoice
(C: 10% ASR), because the owner did say "pay this invoice" and the payee came from the document. You
need provenance *and* a constitution.

**4. "Did you run it on the real model? And is 0% real?"**

Two answers. On the model: the harness runs with a simulated model by default so the demo is offline
and reproducible; the real run is `--model meta` and lands by day 7. On the 0%: **it is conditional on
correct labels, and the corpus shares the router's assumptions, so it is a harness property, not a
security claim.** The falsifiable numbers are in the label layer — DOM hidden-text recall 81.0%
[66.7–90.0], false positives 14.3% [6.3–29.4] — and in the adaptive corpus, where forged sensor
signals produce 80% label error and 20% execution. I report those, not the zero. A browser labeler
using computed styles scores 42/42 with 0/35 false positives on the same cases — an upper bound, but
the reason the production design asks the rendering engine instead of parsing `style=` strings. Scene
text: synthetic signs, OCR detection 94.3% / CER 9.4% (rotated 60%), pipeline executes 0/35 and
produces 24/35 receipts — enforcement does not depend on OCR.

**5. "What about voice cloning?"**

It's a real limitation and I name it. The identity gate is one layer: pair it with device proximity,
a liveness challenge, and policy caps, and require confirmation on irreversible actions. The point of
the architecture is that a failed identity check degrades to *data*, not to *execute*.

**6. "Always-on capture plus voiceprints is exactly what people are suing Meta over."**

Design it out: embeddings stay on-device and are never uploaded; audio is not retained unless the user
saves a receipt; the recording indicator stays; receipts are user-owned. This is the privacy posture
Meta already announced (Confidential VM, private processing) applied to the authority layer.

**7. "Is this a product or a feature?"**

A layer. Voice + scene + DOM provenance, a constitution editor, a receipt ledger, per-app scopes,
family mode (multiple speakers on a shared phone — a real next-billion use case), and an SDK for
WebMCP tool authors. The consumer surface is "what did my agent do today, and why?" — the thing that
makes an agent trustworthy enough to give a wallet.

**8. "What's the business model?"**

Two paths. Platform: Meta ships it as part of Muse/glasses trust. Startup: agent authority for
enterprises deploying fleets of agents — the same primitives (provenance, policy, receipts) sold as
infrastructure. The hackathon entry is the indie-track proof, not the company.

**9. "Why you?"**

I published the measurement this is built on: an edge-native semantic firewall, Phi-3-mini under a
4.2 GiB ceiling, 600 scenarios, 1,800 generations, zero cloud calls. The headline finding was
negative — JSON-only output was *less* safe than free-form (46.2% vs 17.2% unsafe accepts) — and that
negative result is why the architecture puts deterministic provenance in front of the model instead of
asking a small model to be the sole control. The design follows from my own evidence.

**10. "What would you build with 10 engineers?"**

Quarter 1: ship the WebMCP tool-result provenance envelope — an `authority` field the assistant
enforces. Quarter 2: voice + DOM provenance in the Muse client, receipts on device keys. Quarter 3:
scene provenance behind a flag, family mode. Quarter 4: open the benchmark and publish the corpus.

**11. "What's the biggest risk?"**

Adoption: developers won't set a field they don't have to. That's why the contract must be *default
deny* and signed by the platform, not optional metadata. Second risk: platform teams prefer to wait
for model-level robustness — but adaptive attacks keep beating model-level defenses, and the physical
channel makes the problem worse every quarter.

**12. "How do I know the benchmark isn't gamed?"**

It was, and I fixed it. A reviewer pointed out that the corpus and the router's channel table were
written by the same hand, so "0% attack success" was a tautology. The fixed benchmark reports three
things separately: (1) the label layer's measured error with confidence intervals, (2) ASR conditional
on correct labels — explicitly labelled a harness property, and (3) an **adaptive corpus** where the
attacker controls the signals (cloned voice at score 0.91, a page claiming user-typed text). That last
number is 80% label error and 20% execution. Raw logs, the corpus generator and the failure taxonomy
are published; the negative result is the point.

**13. "How is this different from just adding a confirmation prompt?"**

A prompt is a per-action interruption; a mandate is bounded delegation. The owner says "you may pay
the electrician up to 5,000 until Friday" once, and the agent acts inside that envelope without
interrupting — but the envelope is signed, scoped, capped and expiring, and the receipt cites it
(`R6-mandate`). It's also the thing a merchant needs: Amazon blocked Muse because it cannot tell an
owner-authorised purchase from an agent runaway. The demo signs mandates symmetrically with the
device key; production needs a device public key (Ed25519) and an offline verifier — a design sketch,
not built.

---

**14. "What breaks it?"**

A cloned voice at score 0.91 + spoofed proximity: 12/12 label errors, and 3/15 executions in the
adaptive corpus. A forged `signals` dict is stopped by the signed sensor envelope: 6/6 executions without it, 0/6 with
it. Cloned voice is not stopped — the sensor is honest and the voice is fake. DOM hiding techniques the labeler lacks: 81.0% recall, nine missed. The full table with
severity and status is `docs/limitations.md`. None of these are hidden in the submission.

## If you get a hostile question

- Don't defend the number; defend the *method*. "Here's the protocol, here's the raw log, here's the
  arm that beats me."
- Name the limitation before they do. It converts a challenge into a credibility signal.
- If they ask about a specific attack you haven't tested: "Not in the corpus. It should be — here's
  how I'd add it." Never improvise a claim.

## The sentence to end on

> "Provenance tells you who asked. The constitution tells you whether the argument is safe. The
> receipt proves what happened. You need all three — and I can show you the ablation that proves it."
