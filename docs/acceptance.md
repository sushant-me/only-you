# Acceptance report — verified from a fresh clone

Recorded **2026-10-28 17:52 NPT (11:52 UTC)**. Repo commit verified: **`cd91aa3`** (this file was added
after that verification, so it is one commit behind by construction).

## 1. Fresh clone

```bash
git clone https://github.com/sushant-me/only-you /tmp/accept
cd /tmp/accept && make judge
```

| Check | Result |
|---|---|
| Tests | **119 pass** |
| Self-audit | **67 / 67 pass**, exit 0 |
| Live-server smoke | start `onlyyou web` → mandate → pay → refuse → ledger → merchant verify: **pass** |
| Network needed | none (simulated model; `.env` absent) |
| Tree | clean |

## 2. Live links (at verification time)

| Link | Status |
|---|---|
| https://sushant-me.github.io/only-you/ | 200 |
| `demo-3min.mp4` (175.000 s) | 200 |
| `demo-x-vertical.mp4` (45.000 s) | 200 |
| `demo-fallback.mp4` (82.000 s) | 200 |
| `report.pdf` (2 pages) | 200 |
| `threat-model.md`, `judge-qa.md`, `img/youtube-thumb.jpg` | 200 |
| GitHub repo | public, `"private": false` |
| `.env` tracked | no |

`make preflight` re-runs these: **all checks passed — paste the form.**

## 3. Real-model evidence committed

| Run | Corpus | Undefended | Prompt-only | Provenance-only | Full gate | False refusals |
|---|---|---|---|---|---|---|
| Muse Spark 1.3 | confused deputy (8/12) | 25% | 37.5% | 50% | **0%** | 0% (18/18 receipts) |
| Muse Spark contributor | confused deputy (8/12) | 50% | 37.5% | 50% | **0%** | 0% (18/18 receipts) |
| Muse Spark 1.3 | general (20/20) | 0% | 0% | 0% | **0%** | 5% (36/36 receipts) |

Muse Wonder: scene reading 15/15, 0.0% CER; spoken-command transcription verified on the owner's sample.

## 4. What is verified vs what is pending

Verified here: gate behaviour, provenance labels, Ed25519 mandates + offline verify, receipt chain and
tamper detection, agentic task runner, demo server bounds, scene reading, spoken-command transcription,
CI, self-audit, live deployment.

Pending, and owned by the human: the **voice-over** (film is captioned-silent until the full narration
arrives; `make voice` is tested), the **CV form submission**, and the **X post**. No software work is
blocking any of them.

## 5. Reproduce this report

```bash
git clone https://github.com/sushant-me/only-you && cd only-you
make judge        # 172 tests + smoke + 67-check audit
make preflight    # live links + repo public + submission files
make web          # http://127.0.0.1:8000/?script=full&fakecam=1
```
