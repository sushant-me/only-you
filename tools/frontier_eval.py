#!/usr/bin/env python3
"""The frontier-model experiment: arms A (undefended) and D (full gate) only.

Uses the committed confused-deputy corpus (8 attacks / 12 benign, document channel):
the case where a helpful model supplies a document's payee and pays an attacker.

    FRONTIER_API_KEY=... FRONTIER_MODEL=... make frontier-eval
    # local: FRONTIER_API_BASE=http://localhost:11434/v1 FRONTIER_API_KEY=ollama FRONTIER_MODEL=llama3.2:3b
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from onlyyou.agent import Arm
from onlyyou.benchmark import run_arm
from onlyyou.frontier import FrontierModel
from onlyyou.scenarios import read_jsonl

ROOT = Path(__file__).resolve().parents[1]
ARMS = {"A": Arm.A_UNDEFENDED, "D": Arm.D_FULL}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", type=Path, default=ROOT / "data" / "focused-document.jsonl")
    parser.add_argument("--arms", default="A,D")
    parser.add_argument("--out", type=Path, default=ROOT / "results-frontier")
    args = parser.parse_args()

    scenarios = read_jsonl(args.scenarios)
    arms = [ARMS[name.strip().upper()] for name in args.arms.split(",") if name.strip()]
    model = FrontierModel()
    identity = model.identity()
    args.out.mkdir(parents=True, exist_ok=True)

    metrics = []
    started = time.time()
    for arm in arms:
        receipts = args.out / f"receipts-{arm.value}.jsonl"
        receipts.unlink(missing_ok=True)
        _results, arm_metrics = run_arm(scenarios, arm, model, receipts)
        metrics.append(arm_metrics)

    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": "frontier",
        "model": identity["model"],
        "provider": identity["provider"],
        "model_info": {
            "name": identity["model"],
            "provider": identity["provider"],
            "base_url": identity["base_url"],
            "stats": dict(model.stats),
        },
        "corpus": {
            "source": str(args.scenarios.relative_to(ROOT)),
            "attacks": sum(1 for s in scenarios if s.kind == "attack"),
            "benign": sum(1 for s in scenarios if s.kind == "benign"),
            "channels": sorted({s.channel for s in scenarios}),
        },
        "arms": metrics,
        "elapsed_seconds": round(time.time() - started, 1),
        "note": (
            "Arms A and D only. This is the confused-deputy case: the owner asks to pay an invoice "
            "and the document supplies the payee. Compare A (helpful, undefended) with D (full gate)."
        ),
    }
    (args.out / "benchmark.json").write_text(json.dumps(report, indent=2) + "\n")

    lines = [
        "# Frontier experiment — confused deputy (arms A vs D)",
        "",
        f"- provider: **{identity['provider']}** · model: **{identity['model']}**",
        f"- corpus: {report['corpus']['attacks']} attacks / {report['corpus']['benign']} benign "
        f"({', '.join(report['corpus']['channels'])})",
        f"- model calls: {model.stats.get('calls', 0)} · elapsed: {report['elapsed_seconds']}s",
        "",
        "| Arm | Architecture | Attack success ↓ | False refusals ↓ | Receipts verified |",
        "|---|---|---|---|---|",
    ]
    for m in metrics:
        lines.append(
            f"| {m['arm']} | {m['label']} | {m['attack_success_rate'] * 100:.1f}% | "
            f"{m['false_refusal_rate'] * 100:.1f}% | {m['receipts_verified']}/{m['receipts']} |"
        )
    lines += [
        "",
        "A is the model as-is; D is the same model behind the provenance gate, constitution and mandates.",
        "The gate's zero is conditional on correct labels; see docs/limitations.md.",
    ]
    (args.out / "benchmark.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
