# Frontier experiment — confused deputy (arms A vs D)

- provider: **deepseek** · model: **deepseek-chat**
- corpus: 8 attacks / 12 benign (document)
- model calls: 40 · elapsed: 54.1s

| Arm | Architecture | Attack success ↓ | False refusals ↓ | Receipts verified |
|---|---|---|---|---|
| A | undefended | 50.0% | 0.0% | 0/0 |
| D | full ONLY YOU | 0.0% | 0.0% | 18/18 |

A is the model as-is; D is the same model behind the provenance gate, constitution and mandates.
The gate's zero is conditional on correct labels; see docs/limitations.md.
