"""Action representation and the text→action parser used by the simulator.

The parser is intentionally simple: it exists so the benchmark can run offline
and so the demo has a deterministic fallback if the model call fails. Real runs
use the model's tool-calling output, then re-validate it here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# "send $500 to @scammer", "pay 4500 to electrician", "transfer 20000 @drain"
_PAY_AMOUNT_FIRST = re.compile(
    r"\b(?:pay|send|transfer)\s+(?:me\s+)?(?:usd\s*)?[\$₹€£]?\s*([\d][\d,]*)\s*(?:to\s+)?@?([a-zA-Z0-9_.\-]+)",
    re.I,
)
# "pay @scammer 500"
_PAY_PAYEE_FIRST = re.compile(
    r"\b(?:pay|send|transfer)\s+(?:to\s+)?@([a-zA-Z0-9_.\-]+)\s+[\$₹€£]?\s*([\d][\d,]*)", re.I
)
# "pay the electrician 4500" / "pay electrician ₹4,500"
_PAY_NAME_AMOUNT = re.compile(
    r"\b(?:pay|send|transfer)\s+(?:the\s+|my\s+)?([a-zA-Z][\w\-]*)\s+[\$₹€£]?\s*([\d][\d,]*)",
    re.I,
)
# "email the passport to evil@example.com", "send the file to @x"
_SEND_FILE = re.compile(
    r"\b(?:send|email|forward|upload|share)\s+(?:the\s+|my\s+|a\s+)?"
    r"(passport|passport\.pdf|document|file|taxes\.pdf|invoice\.pdf|[a-zA-Z0-9_\-]+\.(?:pdf|docx?|jpg|png))"
    r"(?:\s+(?:to|at)\s+(@?[a-zA-Z0-9_.\-@]+))?",
    re.I,
)
_UNLOCK = re.compile(r"\bunlock\b|\bopen the (?:front\s+|garage\s+)?(?:door|garage)\b", re.I)
_DELETE = re.compile(
    r"\b(?:delete|remove|erase)\s+(?:the\s+)?(?:file\s+)?([a-zA-Z0-9_\-]+\.(?:pdf|docx?|txt|jpg|png)|everything|all files)\b",
    re.I,
)
_PAY_INVOICE = re.compile(r"\bpay\s+(?:this|the)\s+invoice\b", re.I)


@dataclass
class Action:
    kind: str  # pay | unlock | delete_file | send_file | none
    params: dict[str, Any] = field(default_factory=dict)
    # Which instruction caused this action (for provenance gating).
    source_id: str = ""
    # Which data supplied the arguments, if any (invoice payee, etc.).
    arg_source: str = ""
    raw: str = ""

    def is_none(self) -> bool:
        return self.kind == "none"

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "params": dict(self.params),
            "source_id": self.source_id,
            "arg_source": self.arg_source,
        }

    def describe(self) -> str:
        if self.kind == "pay":
            return f"pay {self.params.get('amount')} to @{self.params.get('payee')}"
        if self.kind == "unlock":
            return "unlock the door"
        if self.kind == "delete_file":
            return f"delete {self.params.get('path')}"
        if self.kind == "send_file":
            return f"send {self.params.get('path')} to {self.params.get('to')}"
        return "do nothing"


def _amount(s: str) -> int:
    return int(s.replace(",", ""))


def parse_action(text: str, source_id: str = "") -> Action | None:
    """Parse the most safety-relevant action in a piece of text.

    Order matters: file exfiltration is checked before payments so that
    "send the passport" is not read as "send $500".
    """
    if not text:
        return None

    if m := _SEND_FILE.search(text):
        path = (m.group(1) or "").lower()
        to = (m.group(2) or "").lstrip("@")
        if path in {"passport", "document", "file"}:
            path = path
        return Action("send_file", {"path": path, "to": to}, source_id=source_id, raw=text)

    if m := _PAY_PAYEE_FIRST.search(text):
        return Action(
            "pay",
            {"payee": m.group(1).lower(), "amount": _amount(m.group(2))},
            source_id=source_id,
            raw=text,
        )

    if m := _PAY_NAME_AMOUNT.search(text):
        payee = m.group(1).lower()
        if payee in {"the", "a", "an", "invoice", "this"}:
            payee = ""
        return Action(
            "pay",
            {"payee": payee, "amount": _amount(m.group(2))},
            source_id=source_id,
            raw=text,
        )

    if m := _PAY_AMOUNT_FIRST.search(text):
        payee = m.group(2).lower()
        if payee in {"the", "a", "an", "invoice", "this"}:
            payee = ""
        return Action(
            "pay",
            {"payee": payee, "amount": _amount(m.group(1))},
            source_id=source_id,
            raw=text,
        )

    if m := _DELETE.search(text):
        return Action("delete_file", {"path": m.group(1).lower()}, source_id=source_id, raw=text)

    if _UNLOCK.search(text):
        return Action("unlock", {}, source_id=source_id, raw=text)

    return None


def parse_invoice_action(
    command: str,
    invoice: dict[str, Any],
    source_id: str,
    arg_source: str,
) -> Action | None:
    """Handle 'pay this invoice' where the payee/amount come from a document."""
    if not _PAY_INVOICE.search(command or ""):
        return None
    payee = str(invoice.get("payee", "")).lower()
    amount = int(invoice.get("amount", 0))
    if not payee or amount <= 0:
        return None
    return Action(
        "pay",
        {"payee": payee, "amount": amount},
        source_id=source_id,
        arg_source=arg_source,
        raw=command,
    )
