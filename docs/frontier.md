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

## Status (honest)

- Adapter, CLI (`--model frontier`), Makefile target and env resolution are implemented and tested.
- No frontier key with credit was available in this environment at the time of writing (the available
  DeepSeek key returned HTTP 402; the GitHub token does not expose GitHub Models), so **no frontier run is
  claimed**. Add any key above and `make bench-frontier` reproduces the table in minutes.
- The existing real-model evidence remains Muse Spark (four runs, committed under `results-real*/`).
