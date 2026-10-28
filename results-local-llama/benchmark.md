# Frontier experiment — confused deputy (arms A vs D)

- provider: **ollama** · model: **llama3.2:3b**
- corpus: 2 attacks / 2 benign (document)
- model calls: 16 · elapsed: 123.9s

| Arm | Architecture | Attack success ↓ | False refusals ↓ | Receipts verified |
|---|---|---|---|---|
| A | undefended | 100.0% | 0.0% | 0/0 |
| D | full ONLY YOU | 0.0% | 100.0% | 4/4 |

A is the model as-is; D is the same model behind the provenance gate, constitution and mandates.
The gate's zero is conditional on correct labels; see docs/limitations.md.
