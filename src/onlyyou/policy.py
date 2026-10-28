"""The constitution: a user-written policy, enforced on every action.

Rules are evaluated in order; DENY beats ASK beats ALLOW. The point is not to
be exhaustive — it is to make the *decision* auditable: every verdict names the
rule it applied and the evidence it saw, which is what the receipt records.

A language-model evaluator can be plugged in for ambiguity (see
`ModelPolicyAdvisor`), but the deterministic rules come first. That ordering is
the lesson of the ETFG 2025 firewall paper: output structure without
deliberation is less safe than no contract at all, so the model must never be
the sole control on an irreversible path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Iterable

from .actions import Action
from .mandates import Mandate
from .provenance import Label


class Decision(str, Enum):
    ALLOW = "allow"
    ASK = "ask"
    DENY = "deny"


@dataclass
class Verdict:
    decision: Decision
    rule: str
    reason: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "rule": self.rule,
            "reason": self.reason,
            "evidence": dict(self.evidence),
        }


@dataclass
class Context:
    contacts: set[str] = field(default_factory=set)
    pay_limit: int = 1000
    confirmed: bool = False
    now: str = ""


RuleFn = Callable[[Action, Context], "Verdict | None"]


@dataclass
class Rule:
    id: str
    description: str
    check: RuleFn


def _pay_unknown(action: Action, ctx: Context) -> Verdict | None:
    if action.kind != "pay":
        return None
    payee = str(action.params.get("payee", "")).lower()
    if payee and payee not in ctx.contacts:
        return Verdict(
            Decision.DENY,
            "R1-payee-not-contact",
            f"@{payee} is not in the owner's contacts",
            {"payee": payee, "contacts": sorted(ctx.contacts)},
        )
    return None


def _pay_large(action: Action, ctx: Context) -> Verdict | None:
    if action.kind != "pay":
        return None
    amount = int(action.params.get("amount", 0))
    if amount > ctx.pay_limit:
        return Verdict(
            Decision.ASK,
            "R2-payment-over-limit",
            f"amount {amount} exceeds the one-tap limit {ctx.pay_limit}",
            {"amount": amount, "limit": ctx.pay_limit},
        )
    return None


def _unlock(action: Action, ctx: Context) -> Verdict | None:  # noqa: ARG001
    if action.kind == "unlock":
        return Verdict(
            Decision.ASK,
            "R3-unlock-requires-confirmation",
            "unlocking is irreversible from the agent's side",
            {"door": "front"},
        )
    return None


def _delete(action: Action, ctx: Context) -> Verdict | None:  # noqa: ARG001
    if action.kind == "delete_file":
        return Verdict(
            Decision.ASK,
            "R4-delete-requires-confirmation",
            "deletion is irreversible",
            {"path": action.params.get("path")},
        )
    return None


def _exfiltrate(action: Action, ctx: Context) -> Verdict | None:  # noqa: ARG001
    if action.kind == "send_file":
        return Verdict(
            Decision.DENY,
            "R5-no-file-exfiltration",
            "files may not leave the device without an explicit export flow",
            {"path": action.params.get("path"), "to": action.params.get("to")},
        )
    return None


DEFAULT_RULES: list[Rule] = [
    Rule("R1-payee-not-contact", "Never pay someone who is not a contact", _pay_unknown),
    Rule("R2-payment-over-limit", "Ask before a payment over the limit", _pay_large),
    Rule("R3-unlock-requires-confirmation", "Ask before unlocking", _unlock),
    Rule("R4-delete-requires-confirmation", "Ask before deleting", _delete),
    Rule("R5-no-file-exfiltration", "Never send files out", _exfiltrate),
]


class Constitution:
    def __init__(self, rules: Iterable[Rule] | None = None) -> None:
        self.rules = list(rules) if rules is not None else list(DEFAULT_RULES)
        self.disabled: set[str] = set()

    def set_enabled(self, rule_id: str, enabled: bool) -> None:
        if not any(rule.id == rule_id for rule in self.rules):
            raise ValueError(f"unknown rule: {rule_id}")
        if enabled:
            self.disabled.discard(rule_id)
        else:
            self.disabled.add(rule_id)

    def to_dicts(self) -> list[dict[str, Any]]:
        return [
            {"id": rule.id, "description": rule.description, "enabled": rule.id not in self.disabled}
            for rule in self.rules
        ]

    def add(self, rule: Rule) -> "Constitution":
        self.rules.append(rule)
        return self

    def evaluate(
        self,
        action: Action,
        ctx: Context,
        labels: list[Label] | None = None,
        mandate: Mandate | None = None,
    ) -> Verdict:
        if action.is_none():
            return Verdict(Decision.ALLOW, "R0-no-action", "nothing to do")

        # Provenance precondition: an action caused by a non-command channel is
        # never allowed, regardless of what the policy says.
        if labels is not None and action.source_id:
            src = next((l for l in labels if l.source_id == action.source_id), None)
            if src is not None and not src.command_capable:
                return Verdict(
                    Decision.DENY,
                    "R0-source-not-authoritative",
                    f"instruction originated from {src.origin.value}, not the owner",
                    {"source_id": src.source_id, "origin": src.origin.value},
                )

        # A valid, scoped, unexpired mandate from the owner is delegation:
        # it authorises this action without another prompt. It never overrides
        # provenance (checked above) and it cannot exceed its scope/cap.
        if mandate is not None:
            return Verdict(
                Decision.ALLOW,
                "R6-mandate",
                f"within the owner's mandate {mandate.id}"
                + (f" ({mandate.note})" if mandate.note else ""),
                {
                    "mandate_id": mandate.id,
                    "scope": mandate.scope,
                    "max_amount": mandate.max_amount,
                    "expires_at": mandate.expires_at,
                },
            )

        verdicts: list[Verdict] = []
        for rule in self.rules:
            if rule.id in self.disabled:
                continue
            v = rule.check(action, ctx)
            if v is not None:
                verdicts.append(v)

        for v in verdicts:
            if v.decision is Decision.DENY:
                return v
        for v in verdicts:
            if v.decision is Decision.ASK:
                return v
        return Verdict(Decision.ALLOW, "R9-allow", "no rule blocks this action")


class ModelPolicyAdvisor:
    """Optional second opinion for ambiguous cases.

    Never the sole control: it may only *raise* the decision (ALLOW -> ASK/DENY),
    never lower a deterministic DENY. This mirrors the ETFG 2025 finding that a
    small evaluator is one layer, not the control.
    """

    def __init__(self, client: Any | None = None) -> None:
        self.client = client

    def advise(self, action: Action, constitution_text: str = "") -> Verdict | None:
        if self.client is None:
            return None
        return None  # wire to ModelClient when the API key is available
