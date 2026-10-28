# Live final — run of show, rehearsal and Q&A

Top 5 per track demo live on **9 Nov**. Assume **3–5 minutes** plus questions, screen-shared. The repo
has already been scored; the final is decided by the demo and the answers. This page is the current
version: it includes the merchant terminal, verification surfaces and the delegation features added after
the first recording.

## Before you present (60 minutes out)

- [ ] `make preflight` green; `make web` running; header badge reads `muse-spark-1.3` (green)
- [ ] Browser at 1600×900, notifications off, one tab per asset:
      1. demo at `/?script=full&fakecam=1` (reset first)
      2. playground `…/playground.html` (static, works even if the server dies)
      3. verifier `…/verify.html` (load sample)
      4. the 3-minute video and the 82-second fallback
      5. the 1-page brief, report and deck
- [ ] `/api/reset` called; header counters at 0
- [ ] A mandate granted (electrician ≤ 5,000) and one receipt already in the ledger, so a QR/verify page
      can be opened without hunting
- [ ] Phone hotspot ready; mic tested; second screen with this doc

## 5-minute run of show (current product)

| Time | Say | Do |
|---|---|---|
| 0:00 | "The film opens with the contrast: undefended DeepSeek pays 50% of the attacker's invoices. The same model behind the gate pays 0%, with 18 of 18 receipts verified." | Play the 4 s opening of the film, pause after card 2 |
| 0:12 | "Your glasses can hear the world. The question is who they obey." | Title over the UI |
| 0:25 | Meta's own quote: "not an enforced security boundary." | Quote card / report |
| 0:30 | "Only the enrolled voice commands; everything else is data." | Point at provenance chips |
| 0:45 | "I delegate: electrician, up to 5,000, with a daily sub-limit." | **8 · grant a mandate**, then mention the card's sub-limit line |
| 1:05 | "A merchant verifies that offline — signature, payee, cap, remaining." | Open `/merchant-page`, **Verify mandate & charge** → `MERCHANT VERIFIED · PAID` |
| 1:25 | "The agent pays without interrupting me, and the receipt cites the mandate." | Back to demo, card shows DONE / R6 |
| 1:40 | "Same spoken command, different invoice — refused because the payee is document text." | **5 · attacker invoice** → BLOCKED / R0 |
| 1:55 | "Poster, TV, hidden page text — read, never obeyed." | beats 3, 2, 4 |
| 2:10 | "Don't trust my UI: scan the receipt or open its verify page." | Open `/verify/<id>`; point at the QR |
| 2:30 | "Export the audit bundle and verify it in your browser, no Python." | `/verify.html` → **load sample** → VERIFIED |
| 2:50 | "One task: browse, read, decide, pay, file, explain." | **run agent task**, then **9 · what did you do today?** |
| 3:15 | Evidence: Muse Spark **25% → 37.5% → 50% → 0%** with the full gate, 0% false refusals; final-code reproduction 0%, 16/16 receipts; 172 tests | benchmark table / report |
| 3:40 | "What breaks it: cloned voice, forged sensor, exposed demo server." | limitations page |
| 4:00 | "With ten engineers: WebMCP provenance, Muse voice+DOM provenance, device-rooted mandates." | roadmap card |
| 4:30 | "Superintelligence is useless if it isn't yours." | End card |

**3-minute cut** if the slot is short: 0:00 hook → 0:30 quote → 0:45 mandate → 1:05 merchant PAID →
1:30 pay + 1:40 refusal → 2:00 poster/TV → 2:20 verify page/QR → 2:40 evidence one-liner → 2:50 close.
The look-alike invoice and the merchant verification are the two beats that must survive.

Rehearse 20 times, timed. If running long, drop the task runner and the policy line before dropping the
refusal or the verification.

## Failure fallbacks

| Failure | Fallback |
|---|---|
| Model API down/slow | Demo runs on the simulated model; say so plainly — the gate is the product |
| Camera unavailable | `?fakecam=1`; provenance is unchanged |
| Server won't start | **Playground** (static, same rules) + the 3-min video; then narrate over the brief |
| A beat fails | Re-run it once; if it fails again, move on and mention the recorded run |
| Screen share dies | Show the video tab and answer from the report; the verifier/playground are static |
| No network at all | Docker + local demo from the laptop; video and brief are local files |

## Fifteen questions, short answers

1. **What is actually new?** The authority layer: provenance labels before the model sees the input,
   signed scoped mandates a merchant verifies offline, and receipts for refusals as well as actions.
   Prior work (Devil in the Lens, Prismata, CaMeL) proposes masks or trust policies; this is the
   enforcement and proof surface a wearable agent needs.
2. **Isn't this just prompt-injection defense?** Filters try to make the model robust. This doesn't ask
   the model to win; it decides what is eligible to be an instruction at all.
3. **What's real vs mocked?** Routing, policy, mandates, receipts, OCR, task runner, benchmark and the
   browser verifier are real code. The payment world is a mock. The model is Muse Spark when a key is
   present, simulated otherwise, and the run stamps which.
4. **How good is speaker verification?** Enrolment + a small spectral voiceprint; not anti-spoofing. A
   cloned voice passes. Published as a known failure.
5. **What's the 20% adaptive failure?** When the attacker controls the signals and the owner is present
   and confirms, it gets through 20%. That's why mandates bound the damage and receipts make it visible.
6. **Why would Meta ship this?** Agentic commerce needs merchant-verifiable authorisation; glasses need
   a wearer-vs-world trust story. WebMCP's authority hint is a small change with a large effect.
7. **Does it work offline?** Gate, policy, mandates, receipts, playground and browser verifier are local
   and deterministic. No open-weights deployment was run, so the open-weights bonus is not claimed.
8. **Latency?** Gate ≈0.1 ms in-process; OCR ~200 ms; the model call dominates. The report separates them.
9. **Privacy?** Voiceprints are special-category data; on-device, no audio retained, consent/retention
   flows not built — named in the limitations.
10. **Can a merchant forge a mandate?** No device key, no signature. They can replay a valid one within
    cap/expiry; nonce + ledger tracking bounds it, replay protection is the next step.
11. **Can one agent delegate to another?** Yes: sub-mandates can only narrow payees, cap, expiry and
    period; spending consumes every ancestor; undo refunds the chain.
12. **What about recurring and scheduled payments?** Recurring mandates give a per-period allowance that
    resets; scheduled instructions re-check a live mandate at run time and block + alert if it's invalid.
13. **How do I verify without your server?** `tools/verify_audit.py` in Python, or `verify.html` in the
    browser with WebCrypto — same checks: HMAC receipt chain and Ed25519 mandate signatures.
14. **What surprised you?** Refusals are the product. Users trust an agent that explains what it declined
    more than one that never fails.
15. **Why you?** The ETFG 2025 firewall paper is the same problem one layer down; this is the wearable
    version, built and measured — plus the honesty that the layer is conditional on its labels.

## Closing line

> "Everyone is building agents that can do things. This is the one you can hand your wallet to."
