# Build log

Event window: **26 Oct 2026 12:00 PM ET → 4 Nov 2026 9:00 PM ET**.
Submission: CV platform + 3-minute demo video + public GitHub repo.

This log is the honest record of what was built when. It exists because the rules ask that the demo
show what was built during the event.

## 2026-10-27 — planning day

- Read the kickoff rules and prize structure.
- Fixed the target: Top 5 indie track (live final 9 Nov) + the $5K Best Agentic Use-Case bonus.
- Chose the project: ONLY YOU — provenance-gated authority for wearable agents.
- Wrote the 7-day plan and the 3-minute video shot list.
- Set up the repo and the Meta Model API environment.

## 2026-10-28 — scaffold, tooling, first real call

- Imported the pre-event prototype as a labelled scaffold: `scaffold: pre-event prototype`.
  The provenance/action-gate skeleton, tests and demo existed before kickoff; they are the starting
  point, not the submission. Everything below is event work.
- Added the event repo: README, `.env.example`, `tools/smoke_meta.py`, `make smoke`.
- Verified the test suite runs from a clean checkout (69 tests).
- Added `make smoke` (`tools/smoke_meta.py`): dry-run, `--call`, `--list-models`.
- Wired model selection in the web demo: `MetaModelClient` when `META_API_BASE` +
  `META_API_KEY` are set, otherwise the simulated model (with a log line saying which).
- **Next:** first real Muse Spark call, then run the corpus against the real model.

## Template for the remaining days

```
## 2026-10-29 — <one line theme>

- What was built / changed
- Evidence: command, screenshot, benchmark result
- What broke / what is next
```
