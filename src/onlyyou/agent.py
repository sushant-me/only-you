"""The agent loop: route -> propose -> gate -> execute -> receipt.

The architecture is the argument. The model never sees an unlabelled token
when provenance mode is on, and the gate never trusts the model's account of
why it acted.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .actions import Action, parse_action
from .mandates import MandateLedger
from .model import ModelClient, Observation
from .policy import Constitution, Context, Decision, Verdict
from .provenance import Label, ProvenanceRouter
from .receipts import Receipt, ReceiptLedger
from .tools import MockWorld, ToolResult


class Arm(str, Enum):
    A_UNDEFENDED = "A"
    B_PROMPT_ONLY = "B"
    C_PROVENANCE_ONLY = "C"
    D_FULL = "D"


@dataclass
class RunResult:
    scenario_id: str
    arm: str
    channel: str
    kind: str
    action: Action | None
    verdict: Verdict
    outcome: str  # executed | asked | blocked | noop
    tool_result: ToolResult | None = None
    receipt: Receipt | None = None
    receipt_ok: bool = False
    latency_ms: float = 0.0
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "arm": self.arm,
            "channel": self.channel,
            "kind": self.kind,
            "action": self.action.to_dict() if self.action else None,
            "verdict": self.verdict.to_dict(),
            "outcome": self.outcome,
            "tool_result": self.tool_result.detail if self.tool_result else None,
            "receipt_id": self.receipt.id if self.receipt else None,
            "receipt_ok": self.receipt_ok,
            "latency_ms": round(self.latency_ms, 3),
        }


class Agent:
    def __init__(
        self,
        model: ModelClient,
        router: ProvenanceRouter,
        world: MockWorld,
        constitution: Constitution | None = None,
        ledger: ReceiptLedger | None = None,
        mandates: MandateLedger | None = None,
    ) -> None:
        self.model = model
        self.router = router
        self.world = world
        self.constitution = constitution or Constitution()
        self.ledger = ledger
        self.mandates = mandates

    def run(self, scenario: Any, arm: Arm) -> RunResult:
        t0 = time.perf_counter()
        labels = self.router.route(scenario.inputs)

        mode = "raw" if arm in (Arm.A_UNDEFENDED, Arm.B_PROMPT_ONLY) else "labeled"
        obs = Observation(mode=mode, labels=labels, owner_command=scenario.owner_command)
        action = self.model.propose(obs, arm.value) or Action(kind="none")

        # Evidence enrichment: when the model pays an invoice, attribute the
        # *arguments* to the document that supplied them even if the model did
        # not say so. The instruction still comes from the owner.
        if action.kind == "pay" and not action.arg_source:
            payee = str(action.params.get("payee", "")).lower().lstrip("@")
            try:
                amount = int(action.params.get("amount", 0) or 0)
            except (TypeError, ValueError):
                amount = 0
            for label in labels:
                if label.command_capable:
                    continue
                invoice = label.input.signals.get("invoice")
                if not invoice:
                    continue
                doc_payee = str(invoice.get("payee", "")).lower().lstrip("@")
                if doc_payee == payee and int(invoice.get("amount", 0) or 0) == amount:
                    action.arg_source = label.source_id
                    break

        ctx = Context(
            contacts=set(self.world.contacts),
            pay_limit=scenario.pay_limit,
            confirmed=scenario.owner_confirms,
        )

        receipt = None
        receipt_ok = False
        tool_result = None
        evidence: dict[str, Any] = {}
        neutral = self._first_data_instruction(labels) if action.is_none() else None

        mandate = None
        if (
            arm is Arm.D_FULL
            and self.mandates is not None
            and not action.is_none()
        ):
            found, _why = self.mandates.find_covering(action.to_dict())
            mandate = found

        if neutral is not None and arm is Arm.D_FULL and self.ledger is not None:
            # Nothing executed, but an environment-originated instruction was
            # attempted. Record it: the receipt is the product's memory of what
            # the agent *refused* to do, not only what it did.
            label, parsed = neutral
            verdict = Verdict(
                Decision.DENY,
                "R0-instruction-from-data",
                f"instruction from {label.origin_label} was treated as data; no action taken",
                {"source_id": label.source_id, "origin": label.origin.value},
            )
            outcome = "blocked"
            action = parsed
            evidence = self._evidence(action, labels)
            evidence["proposed_by"] = "display_only"
            receipt = self.ledger.append(
                action=action.to_dict(),
                verdict=verdict.to_dict(),
                evidence=evidence,
                result={"outcome": "blocked", "detail": "refused"},
            )
            receipt_ok = self.ledger.verify(receipt)
        else:
            verdict = self._verdict(action, labels, ctx, arm, mandate)
            outcome, tool_result = self._apply(action, verdict, scenario)
            if outcome == "executed" and mandate is not None and action.kind == "pay":
                self.mandates.consume(
                    mandate,
                    int(action.params.get("amount", 0)),
                    payee=str(action.params.get("payee", "")),
                )
            evidence = self._evidence(action, labels)
            evidence["proposed_by"] = "model"
            if verdict.evidence.get("mandate_id"):
                evidence["mandate"] = {
                    "id": verdict.evidence["mandate_id"],
                    "max_amount": verdict.evidence.get("max_amount"),
                    "expires_at": verdict.evidence.get("expires_at"),
                }
                if mandate is not None:
                    evidence["mandate"]["remaining_after"] = self.mandates.remaining(mandate)
            if arm is Arm.D_FULL and self.ledger is not None and not action.is_none():
                receipt = self.ledger.append(
                    action=action.to_dict(),
                    verdict=verdict.to_dict(),
                    evidence=evidence,
                    result={"outcome": outcome, "detail": tool_result.detail if tool_result else ""},
                )
                receipt_ok = self.ledger.verify(receipt)

        latency_ms = (time.perf_counter() - t0) * 1000.0
        return RunResult(
            scenario_id=scenario.id,
            arm=arm.value,
            channel=scenario.channel,
            kind=scenario.kind,
            action=None if action.is_none() else action,
            verdict=verdict,
            outcome=outcome,
            tool_result=tool_result,
            receipt=receipt,
            receipt_ok=receipt_ok,
            latency_ms=latency_ms,
            evidence=evidence,
        )

    # -- neutralised instructions -----------------------------------------
    @staticmethod
    def _first_data_instruction(labels: list[Label]) -> tuple[Label, Action] | None:
        for label in labels:
            if label.command_capable:
                continue
            parsed = parse_action(label.text, label.source_id)
            if parsed is not None:
                return label, parsed
        return None

    # -- gate --------------------------------------------------------------
    def _verdict(
        self,
        action: Action,
        labels: list[Label],
        ctx: Context,
        arm: Arm,
        mandate: Any | None = None,
    ) -> Verdict:
        if action.is_none():
            return Verdict(Decision.ALLOW, "R0-no-action", "nothing to do")

        if arm in (Arm.A_UNDEFENDED, Arm.B_PROMPT_ONLY):
            return Verdict(Decision.ALLOW, "R-none", "no enforcement layer")

        src = next((l for l in labels if l.source_id == action.source_id), None)
        if src is None:
            return Verdict(Decision.DENY, "R0-unknown-source", "action has no provenance")
        if not src.command_capable:
            return Verdict(
                Decision.DENY,
                "R0-source-not-authoritative",
                f"instruction came from {src.origin_label}, not the owner",
                {"source_id": src.source_id, "origin": src.origin.value},
            )

        if arm is Arm.C_PROVENANCE_ONLY:
            return Verdict(
                Decision.ALLOW,
                "R0-owner-authorised",
                "instruction came from the owner; no policy layer",
                {"source_id": src.source_id},
            )

        return self.constitution.evaluate(action, ctx, labels, mandate)

    # -- execution ---------------------------------------------------------
    def _apply(
        self, action: Action, verdict: Verdict, scenario: Any
    ) -> tuple[str, ToolResult | None]:
        if action.is_none():
            return "noop", None
        if verdict.decision is Decision.DENY:
            return "blocked", None
        if verdict.decision is Decision.ASK:
            if not scenario.owner_confirms:
                return "asked", None
            return "executed", self.world.execute(action)
        return "executed", self.world.execute(action)

    # -- evidence ----------------------------------------------------------
    @staticmethod
    def _evidence(action: Action, labels: list[Label]) -> dict[str, Any]:
        src = next((l for l in labels if l.source_id == action.source_id), None)
        arg = next((l for l in labels if l.source_id == action.arg_source), None)
        ev: dict[str, Any] = {}
        if src is not None:
            ev["instruction"] = {
                "source_id": src.source_id,
                "origin": src.origin.value,
                "text": src.text[:200],
            }
        if arg is not None:
            ev["argument_source"] = {
                "source_id": arg.source_id,
                "origin": arg.origin.value,
                "text": arg.text[:200],
            }
        ev["params"] = action.params
        return ev
