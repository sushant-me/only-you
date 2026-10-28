# Open-weights entry — plan

> **Status: not shipped.** No open-weights deployment ran, so this category is **not claimed**. The plan
> below is kept for the finalist round; do not check the box unless the logs land in `results-open/`.

Prize: **$10K Best Build on Meta Open Weights** (Muse Glimmer or Muse Spark Open, on your own hardware or
partner inference). This is optional; submit only if it actually runs.

## The angle

ONLY YOU's argument is that **authority must not depend on the frontier model**. The provenance gate,
constitution and receipts are local and deterministic. For this prize, the *only* model call — the
ambiguity evaluator — moves to **open weights**. That makes the strongest version of the claim:

> the trust layer still enforces and receipt the owner's authority when the frontier model is unavailable.

## Steps (≈2 hours once credits are in hand)

1. **Claim credits** — Baseten ($100) or Modal ($100) request forms in `#resources`.
2. **Deploy Muse Glimmer** (or Muse Spark Open) on the partner:
   - Baseten: deploy from the model catalog / `truss`; note the endpoint URL and API key.
   - Modal: deploy an OpenAI-compatible endpoint (`modal deploy`, `@app.function` serving `/v1/chat/completions`).
   - Fireworks: create a deployment; copy base URL + key.
3. **Wire it** — the adapter is already generic (OpenAI-compatible); only env changes:

```bash
export OPEN_WEIGHTS_BASE=https://.../v1        # from the deployment
read -rs OPEN_WEIGHTS_KEY && export OPEN_WEIGHTS_KEY   # paste at the prompt, not in the shell history
export OPEN_WEIGHTS_MODEL=muse-glimmer
make bench-open LIMIT=10     # cheap sanity run first
```

4. **Measure** — latency p50/p95, tokens, and the four-arm table on the subset. Record in
   `results-open/` and copy the summary into `docs/open-weights-results.md`.
5. **Record 20 seconds** — the same beats, with `--model open`, showing the evaluator badge. Add to the
   video only if it is real.
6. **Submit** under the open-weights category in the CV form.

## Fallbacks

| Situation | Action |
|---|---|
| No endpoint available | Skip the category; keep the frontier build |
| Endpoint too slow / rate-limited | Use a 10-scenario subset; report latency honestly |
| Only quantized weights, own GPU | `vllm` or `llama.cpp` server exposing `/v1/chat/completions`; point `OPEN_WEIGHTS_*` at it |
| Model id different | `OPEN_WEIGHTS_MODEL` is just a string; use the deployment's id |

## Honesty rules

- Do not submit this category unless the run is real and the logs are in `results-open/`.
- Do not claim "fully offline" if the endpoint is a hosted partner — say "open-weights model".
- If it does not ship, the report and deck already describe the design; that is enough.
