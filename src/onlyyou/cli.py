"""Command line entry points.

    python -m onlyyou.cli gen      --out data/scenarios.jsonl
    python -m onlyyou.cli bench    --model simulated --out results
    python -m onlyyou.cli bench    --model meta      --out results-real
    python -m onlyyou.cli demo
    python -m onlyyou.cli verify   --ledger results/receipts-D.jsonl
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from pathlib import Path

from .agent import Agent, Arm
from .env import load_env
from .model import SimulatedModel
from .policy import Constitution
from .provenance import ProvenanceRouter, render_labeled
from .receipts import DEMO_SECRET, ReceiptLedger
from .scenarios import generate, read_jsonl, write_jsonl
from .tools import MockWorld

DEMO_ATTACK = "atk-doc-invoice-00"
DEMO_BENIGN = "ben-doc-invoice-00"


def _demo() -> int:
    scenarios = {s.id: s for s in generate()}
    attack = scenarios[DEMO_ATTACK]
    # find a benign invoice scenario (ids are generated in order)
    benign = next(s for s in scenarios.values() if s.id.startswith("ben-doc-") and s.goal == "pay")

    for scenario in (benign, attack):
        world = MockWorld()
        ledger = ReceiptLedger(DEMO_SECRET)
        agent = Agent(SimulatedModel(), ProvenanceRouter(), world, Constitution(), ledger)
        labels = agent.router.route(scenario.inputs)
        result = agent.run(scenario, Arm.D_FULL)

        print("=" * 72)
        print(f"{scenario.kind.upper():<7} {scenario.id}  channel={scenario.channel}")
        print("-" * 72)
        print("routed observation:")
        print(render_labeled(labels))
        print("-" * 72)
        print(f"agent proposed : {result.action.describe() if result.action else 'nothing'}")
        print(f"gate verdict   : {result.verdict.decision.value} ({result.verdict.rule}) — {result.verdict.reason}")
        print(f"outcome        : {result.outcome}")
        if result.receipt:
            print(f"receipt        : {result.receipt.id} verified={result.receipt_ok}")
            print(f"evidence       : {json.dumps(result.evidence, indent=2)[:600]}")
        print(f"world          : {json.dumps(world.snapshot())}")
    print("=" * 72)
    return 0


def _verify(path: str) -> int:
    ledger = ReceiptLedger(DEMO_SECRET, path)
    ok = ledger.verify_chain()
    print(f"receipts: {len(ledger.receipts)}  chain_ok={ok}")
    for r in ledger.receipts:
        print(f"  {r.id}  {r.verdict.get('decision')}  {r.action.get('kind')}  sig_ok={ledger.verify(r)}")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="onlyyou", description="ONLY YOU starter kit")
    sub = parser.add_subparsers(dest="cmd", required=True)

    gen = sub.add_parser("gen", help="generate and write the scenario corpus")
    gen.add_argument("--out", default="data/scenarios.jsonl")

    bench = sub.add_parser("bench", help="run the four-arm benchmark")
    bench.add_argument("--model", choices=["simulated", "meta", "open"], default="simulated")
    bench.add_argument("--arms", default="A,B,C,D")
    bench.add_argument("--out", default="results")
    bench.add_argument("--scenarios", default=None)
    bench.add_argument("--limit", type=int, default=None, help="cap attacks and benign scenarios (quick runs)")

    sub.add_parser("demo", help="narrate one benign and one attack scenario")

    scenes = sub.add_parser("scenes", help="render signs, OCR them, route the result")
    scenes.add_argument("--out", default="results/scene-eval.json")

    web = sub.add_parser("web", help="serve the local demo UI")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8000)

    ver = sub.add_parser("verify", help="verify a receipt ledger")
    ver.add_argument("--ledger", required=True)

    args = parser.parse_args(argv)

    if args.cmd == "gen":
        scenarios = generate()
        path = write_jsonl(args.out, scenarios)
        attacks = sum(1 for s in scenarios if s.kind == "attack")
        print(f"wrote {len(scenarios)} scenarios ({attacks} attacks) to {path}")
        return 0

    if args.cmd == "bench":
        from .benchmark import print_summary, run_benchmark

        load_env()

        arms = [Arm(a.strip().upper()) for a in args.arms.split(",") if a.strip()]
        scenarios = read_jsonl(args.scenarios) if args.scenarios else None
        report = run_benchmark(args.model, arms, args.out, scenarios, limit=args.limit)
        print_summary(report)
        print(f"\nreport: {Path(args.out) / 'benchmark.md'}")
        return 0

    if args.cmd == "demo":
        return _demo()

    if args.cmd == "scenes":
        from .scene_eval import evaluate

        report = evaluate()
        pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps({k: report[k] for k in ("available", "n", "detection_rate", "mean_cer")}, indent=2))
        return 0

    if args.cmd == "web":
        from .webapp import serve

        serve(args.host, args.port)
        return 0

    if args.cmd == "verify":
        return _verify(args.ledger)

    return 2


if __name__ == "__main__":
    sys.exit(main())
