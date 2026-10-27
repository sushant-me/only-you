# `untrustedContentHint` is not a boundary

### A provenance contract for WebMCP tool results

*Draft note — publish before the hackathon, link it in the submission.*

---

Meta's WebMCP page for Ray-Ban Display developers contains an unusually candid sentence:

> "Set `untrustedContentHint` honestly, since **it's not an enforced security boundary**."
> — [Meta Wearables Developers, WebMCP agent tools](https://wearables.developer.meta.com/docs/develop/webapps/agent-tools)

The same page warns that "your tool's result text goes into the assistant's context, so returning
unmarked untrusted content is how a prompt injection reaches the model," that "Meta AI chooses the
arguments" and "nothing guarantees they match your `inputSchema`," and that developers should "never
take a destructive or irreversible action solely because a tool was called with plausible-looking
arguments."

Read together, these are not implementation notes. They are a threat model written by the company
shipping both the assistant and the glasses — and a description of a gap: **the platform knows the
provenance of tool results and declines to enforce it.**

That is a reasonable engineering choice today. It is not a stable one. WebMCP is rolling out to
Ray-Ban Display ("off by default and enabled per device"), the assistant is gaining payments and
shopping, and the same class of input is now arriving through a camera and a microphone. A hint that
well-behaved developers set correctly protects nobody from a developer who does not — and prompt
injection is, by construction, the attack that arrives through the channel you do not control.

## Why a hint cannot be a boundary

A security boundary needs three properties: it is **enforced** by a component the attacker cannot
bypass, it is **verifiable** by the party relying on it, and it is **default-deny** for the risky
case. `untrustedContentHint` has none of the three. It is advisory (a developer may omit or
mislabel it), unverifiable (the assistant cannot tell a correct hint from an incorrect one), and
default-allow (unmarked content is treated as ordinary text).

The consequence is the confused-deputy pattern that has already been demonstrated against wearable
VLMs: text in the environment — a poster, a TV subtitle, a shirt, an invoice — is read into the
assistant's context and interpreted as an instruction. Published work reports attack success rates
up to 96% in simulation and 60% in real environments against current models
([Devil in the Lens, 2026](https://arxiv.org/abs/2607.10269)). The web analogue is equally
documented ([Prismata, 2026](https://arxiv.org/abs/2607.08147)).

## The contract

Replace the hint with a **signed origin envelope** attached to every tool result, and make the
assistant's planner treat it as data by default. Sketch:

```json
{
  "tool": "shop.lookup",
  "result": "…text the model may read…",
  "origin": {
    "publisher": "merchant.example",      // who produced the content
    "channel": "webmcp.tool_result",      // how it reached the assistant
    "authority": "none",                  // none | owner | system
    "surface": "product_review",           // optional: review / ad / listing / doc
    "issued_at": "2026-10-26T12:00:00Z",
    "nonce": "b64…",
    "sig": "ed25519:…"                     // over the canonical envelope
  }
}
```

Three enforcement rules make it a boundary:

1. **Authority is a property of the envelope, not of the text.** Only envelopes with
   `authority: owner` (produced by the wearer's own device, under the wearer's key) may populate the
   planner's instruction channel. Everything else is context, however imperative it sounds.
2. **Arguments derived from unverified content are capabilities, not instructions.** If the owner
   says "pay this invoice," the payee is still untrusted data: it may fill an argument only within a
   capability the owner granted (a payee allow-list, an amount cap), and any irreversible action
   requires an explicit confirmation that shows the evidence.
3. **Every executed action emits a receipt** binding `{action, arguments, envelope hashes, rule,
   decision}` under the device key. The page and the wearer can verify it; the assistant cannot
   silently rewrite history.

Rules 1 and 2 are enforcement; rule 3 is the part that makes trust legible to a human — and the part
that no shipping assistant currently provides.

## Reference implementation

`only-you` (this repo) implements the contract end-to-end for a mock agent: channel provenance
(voice / scene / DOM / document), a constitution gating irreversible actions, and HMAC-signed,
hash-chained receipts. It runs offline with no API key. Swapping the mock model for the Meta Model
API is one environment variable.

The benchmark is deliberately two-sided: attacks blocked **and** false refusals on benign commands.
A defense that blocks everything is not a defense; it is a product that users turn off.

## What this note is not

It is not a vulnerability disclosure. Everything described here is stated in Meta's own developer
documentation, and the attacks cited are published research. It is a proposal: make the sentence
"it's not an enforced security boundary" obsolete by giving the platform an enforceable alternative
that developers can adopt without changing their tools.

The glasses are going to hear the world. They should know who is allowed to speak to them.

---

## Publish checklist

- [ ] Push the repo with this note at `docs/webmcp-note.md`; pin the repo.
- [ ] Publish the note as a post (dev.to / Substack / Hashnode / GitHub Pages) — you need a URL.
- [ ] Post once on LinkedIn and once on X with the quote card and the demo screenshot.
- [ ] Tag `@AIatMeta` and `@MetaforDevs` once. No follow-up tagging.
- [ ] Send it to the engineers named on Meta's WebMCP page — as a feedback request, not a job ask.
- [ ] Never frame it as a vulnerability or an attack on Meta. It is a contract proposal plus a
      reference implementation.
