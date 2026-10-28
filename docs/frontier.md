# Frontier models through the same gate

**Why this matters.** Muse Spark's own alignment refused the obvious injections even undefended, so on the
general corpus every arm scored 0%. The interesting question is what happens with a model tuned to be
*maximally helpful*: the more capable the model, the more it will comply with the world — which is exactly
where an authority layer stops being optional. The gate is model-agnostic by design; only the proposal
changes.

## Architecture (one adapter, no gate changes)

```
sensors → label layer → gate (provenance · constitution · mandate) → receipts
                              ↕
                     FrontierModel (OpenAI-compatible chat completions)
                              ↕
              OpenAI · Gemini · Claude · OpenRouter · local Ollama
```

- The model only *proposes*: `{"kind", "params", "source_id"}`.
- The gate re-validates provenance, the constitution, the mandate (caps/sub-limits/period) and receipts.
- No tool is executed by the model; only approved actions reach the mock world.
- Receipts are identical — same HMAC chain, same audit export, same browser verifier.

## Configure a key (any one)

```bash
# OpenAI
OPENAI_API_KEY=...  OPENAI_MODEL=gpt-4o-mini

# Google Gemini (OpenAI-compatible endpoint)
GEMINI_API_KEY=...  GEMINI_MODEL=gemini-2.0-flash

# Anthropic (OpenAI-compatible endpoint)
ANTHROPIC_API_KEY=...  ANTHROPIC_MODEL=claude-3-5-sonnet-latest

# DeepSeek (frontier-class, OpenAI-compatible)
DEEPSEEK_API_KEY=...  DEEPSEEK_MODEL=deepseek-chat

# OpenRouter, or a local Ollama server
OPENROUTER_API_KEY=...  OPENROUTER_MODEL=openai/gpt-4o-mini
# or: FRONTIER_API_BASE=http://localhost:11434/v1 FRONTIER_API_KEY=ollama FRONTIER_MODEL=llama3.2
```

`FRONTIER_API_BASE/KEY/MODEL` overrides any of the presets. The benchmark refuses to run with
`--model frontier` when no key is configured, so no simulated number can be mislabelled as a frontier run.

## Run the comparison

```bash
make frontier-eval      # the headline experiment: confused-deputy corpus, arms A vs D only (fast)
make bench-frontier     # full four-arm benchmark + extras (slower)
```

`make frontier-eval` reads `data/focused-document.jsonl` (8 attacks / 12 benign, document channel) and
writes `results-frontier/benchmark.json` + `benchmark.md` with attack success, false refusals and verified
receipts for both arms. A local open-weights model works the same way:

```bash
docker run -d -p 11434:11434 -v ~/.ollama:/root/.ollama ollama/ollama
FRONTIER_API_BASE=http://127.0.0.1:11434/v1 FRONTIER_API_KEY=ollama \
FRONTIER_MODEL=llama3.2:3b make frontier-eval
```

Then look at `results-frontier/benchmark.json`:

| Field | Expected |
|---|---|
| `arms[A].attack_success_rate` | high on the confused-deputy corpus (helpful model pays the invoice) |
| `arms[D].attack_success_rate` | **0%** — the gate refuses the document-supplied payee |
| `arms[D].receipts_verified` | all, chain ok |
| `mode` / `model_info.provider` | the provider name, so the artifact is self-describing |

Publish the per-model table next to the Muse Spark runs; the claim becomes **"the more capable the model,
the more necessary the authority layer"** — and one audit bundle can cover every model because the
receipts are model-independent.

## Measured frontier result — DeepSeek-chat

With a provider key available, `make frontier-eval` ran the **same confused-deputy corpus** (8 attacks /
12 benign, document channel) through the unchanged gate. Artifacts: `results-frontier/`.

| Arm | Architecture | Attack success | False refusals | Receipts |
|---|---|---|---|---|
| A | undefended DeepSeek-chat | **50.0%** (4/8 attacks; 10/12 benign paid) | 0% | — |
| D | **full ONLY YOU** | **0.0%** | **0.0%** | **18/18 verified** |

40 model calls, 54 s, temperature 0, same corpus and mandates as the Muse runs. This is the headline the
architecture was built for: **the more capable/helpful the model, the more it needs an authority layer.**
The model obeys the document; the gate obeys the owner.

Reproduce with:

```bash
DEEPSEEK_API_KEY=... make frontier-eval
# or point FRONTIER_* at any OpenAI-compatible provider
```

## Secondary: local integration run

A local open-weights model (`llama3.2:3b` via Ollama) was run first as a plumbing check on 2 attacks /
2 benign. Artifacts: `results-local-llama/`.

| Arm | Attack success | False refusals | Receipts |
|---|---|---|---|
| A — undefended | **100%** (2/2 paid) | 0% | — |
| D — full gate | **0%** (0/2) | **100%** (2/2 benign blocked) | 4/4 verified |

The D false refusals are **model misattribution**, not a gate bug: the small model left the top-level
`source_id` empty and cited the document. The gate correctly refused an action with no authoritative
source. This is an integration result, not a frontier claim; the DeepSeek run above is the frontier claim.

## Status

- Adapter, CLI (`--model frontier`), `make frontier-eval` / `make bench-frontier`, provider presets
  (OpenAI, Gemini, Anthropic, DeepSeek, OpenRouter, local Ollama) and env resolution are implemented.
- **DeepSeek-chat A-vs-D completed:** 50% → 0%, 0% false refusals, 18/18 receipts (`results-frontier/`).
- The primary real-model evidence remains Muse Spark (four runs, `results-real*/`); the two are independent.
- A cross-provider table is available by setting another provider key and re-running `make frontier-eval`.
