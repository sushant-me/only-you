# Live final — run of show and Q&A

Top 5 per track demo live on **9 Nov**. Assume 3–5 minutes per team plus questions, and a screen
share. This is the highest-leverage 5 minutes of the event: the judges have already scored the repo;
the final is decided by the demo and the answers.

## Before you present (60 minutes out)

- [ ] `make web` running; browser at 1600×900; `?fakecam=1` ready
- [ ] `/api/reset` called; header counts at 0
- [ ] A pre-recorded 90-second screen capture open in a second tab (fallback)
- [ ] The 3-minute video open in a third tab (if screen share fails)
- [ ] Report and benchmark open in a PDF/editor
- [ ] Phone hotspot ready; microphone tested; notifications off
- [ ] This doc open on a second screen, scrolled to the Q&A

## 5-minute run of show

| Time | Say | Do |
|---|---|---|
| 0:00 | "Your glasses can hear the world. The question is who they obey." | Title over the UI |
| 0:15 | Meta's own quote: "not an enforced security boundary" | Quote card / report page |
| 0:35 | "Three primitives: identity, mandates, receipts." | Point at the constitution panel |
| 0:50 | "Grant a mandate: electrician, up to 5,000, until tomorrow." | Click **8 · grant a mandate** |
| 1:05 | "Now it can pay without asking me twice." | Click **1 · owner pays invoice** → DONE/R6 card |
| 1:25 | "Same spoken command, different invoice." | Click **5 · attacker invoice** → BLOCKED/R1 |
| 1:40 | "Poster." | Click **3 · poster** → mask + BLOCKED/R0 |
| 1:50 | "TV, hidden page text — same result." | Click **2 · TV ad**, **4 · hidden page text** |
| 2:05 | "And it can run a whole task: browse, read, decide, pay, file a receipt." | Click **run agent task**; let the step trace fill |
| 2:35 | "Ask it what it did." | Click **9 · what did you do today?** |
| 2:50 | Evidence: label layer 81%/14.3%, adaptive 20% still gets through, forged 6/6→0/6 | Benchmark table |
| 3:20 | "Merchant-verifiable mandates: Ed25519, offline check." | `tools/mandate_demo.py` output |
| 3:40 | "What breaks it: cloned voice, forged sensor, compromised device." | limitations page |
| 4:00 | "With ten engineers: WebMCP provenance, Muse client voice+DOM, device-key mandates." | Roadmap card |
| 4:30 | "Superintelligence is useless if it isn't yours." | End card |

Rehearse 20 times. Time each run; if you are over 5:00, cut the evidence slide to one number (the
look-alike invoice beat is the one that must survive).

## Failure fallbacks

| Failure | Fallback |
|---|---|
| Model API down/slow | Demo works with the simulated model (the gate is the product); say so plainly |
| Camera unavailable | `?fakecam=1` scene feed; the provenance logic is unchanged |
| Server won't start | Play the pre-recorded 90-second capture, then narrate over the report |
| A beat fails | Re-run that beat once; if it fails again, move on and mention the recorded run |
| Screen share dies | Show the 3-minute video tab and answer questions |

## Fifteen questions, short answers

1. **What is actually new?**
   The authority layer: inputs labelled by provenance before the model sees them, signed scoped
   mandates with an offline merchant verifier, and receipts for refusals as well as actions. Prior
   work (Devil in the Lens, Prismata, CaMeL) proposes masks or trust policies; this is the enforcement
   and proof surface a wearable agent needs.
2. **Isn't this just prompt injection defense?**
   Injection filters try to make the model robust. This doesn't ask the model to win; it decides what
   is eligible to be an instruction at all.
3. **What's real vs mocked?**
   Provenance routing, policy, mandates, receipts, OCR, task runner and benchmark are real code. The
   payment world is a mock. The model is Muse Spark when the key is present, simulated otherwise, and
   the report stamps which mode produced it.
4. **How good is speaker verification?**
   The demo uses enrolment + a small spectral voiceprint. It is not a trained anti-spoofing model; a
   cloned voice passes. We report that as a known failure, not hide it.
5. **What about the 20% adaptive failure?**
   When the attacker controls the signals and the owner is present and confirms, it gets through 20%
   of the time. That's why mandates bound the damage and receipts make it visible.
6. **Why would Meta ship this?**
   Because agentic commerce needs a merchant-verifiable authorisation and glasses need a trust story.
   The WebMCP `authority` field is a small change with a large effect.
7. **Does it work offline?**
   The gate does; the policy evaluator can run on Muse Glimmer open weights. That's the open-weights
   bonus entry.
8. **Latency?**
   Gate ≈0.1 ms in-process; OCR ~200 ms; model call dominates. The report separates them.
9. **Privacy?**
   Voiceprints are special-category data; on-device only, no training on user audio, consent flow and
   retention policy are required before shipping. Named in the limitations.
10. **Can a merchant forge a mandate?**
    No — they can't sign with the device key. They can replay a valid one within its cap/expiry;
    nonce + ledger tracking bounds that, and replay protection is the next engineering step.
11. **What did you build during the event?**
    The Ed25519 mandates, the agentic task runner, scene OCR, the UI, the real-model benchmark
    plumbing and the video. The repo labels the pre-event scaffold commit.
12. **What would you do with 10 engineers?**
    WebMCP provenance envelope, voice+DOM provenance in the Muse client, device-key mandates with an
    offline merchant verifier, scene provenance behind a flag.
13. **What's the business model?**
    Start as the trust layer for agentic checkout (merchant-side verification SaaS), then licence the
    provenance envelope to device makers. The hackathon ask is the pilot, not the business.
14. **What surprised you?**
    That refusals are the product. Users trust an agent that can explain what it declined and why,
    more than one that never fails.
15. **Why you?**
    The ETFG 2025 firewall paper is the same problem one layer down; this is the wearable version of
    that result, built and measured.

## Closing line

> "Everyone is building agents that can do things. This is the one you can hand your wallet to."
