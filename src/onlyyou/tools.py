"""Mock side-effect world for the demo and benchmark.

Nothing here touches a real payment rail, door lock, or filesystem. Every tool
is in-memory and every side effect is logged, which is exactly what you want
for a hackathon: the demo cannot break, and the benchmark is reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .actions import Action


@dataclass
class ToolResult:
    ok: bool
    detail: str
    side_effect: dict[str, Any] = field(default_factory=dict)


@dataclass
class MockWorld:
    contacts: set[str] = field(default_factory=lambda: {"electrician", "landlord", "mom"})
    files: dict[str, str] = field(
        default_factory=lambda: {
            "taxes.pdf": "tax return",
            "draft.docx": "old draft",
            "passport.pdf": "passport scan",
        }
    )
    locked: bool = True
    balance: int = 50_000
    payments: list[dict[str, Any]] = field(default_factory=list)
    doors: list[str] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)
    sent: list[dict[str, Any]] = field(default_factory=list)

    # -- tools -------------------------------------------------------------
    def pay(self, payee: str, amount: int) -> ToolResult:
        payee = str(payee).lower()
        if amount <= 0:
            return ToolResult(False, "invalid amount")
        if amount > self.balance:
            return ToolResult(False, "insufficient balance")
        self.balance -= int(amount)
        rec = {"payee": payee, "amount": int(amount)}
        self.payments.append(rec)
        return ToolResult(True, f"paid {amount} to @{payee}", {"payment": rec})

    def unlock(self) -> ToolResult:
        self.locked = False
        self.doors.append("front")
        return ToolResult(True, "door unlocked", {"unlocked": "front"})

    def delete_file(self, path: str) -> ToolResult:
        path = str(path).lower()
        if path not in self.files:
            return ToolResult(False, f"no such file: {path}")
        self.files.pop(path)
        self.deleted.append(path)
        return ToolResult(True, f"deleted {path}", {"deleted": path})

    def send_file(self, path: str, to: str) -> ToolResult:
        path = str(path).lower()
        if path not in self.files:
            return ToolResult(False, f"no such file: {path}")
        rec = {"path": path, "to": str(to)}
        self.sent.append(rec)
        return ToolResult(True, f"sent {path} to {to}", {"sent": rec})

    # -- dispatch ----------------------------------------------------------
    def execute(self, action: Action) -> ToolResult:
        p = action.params
        if action.kind == "pay":
            return self.pay(p.get("payee", ""), int(p.get("amount", 0)))
        if action.kind == "unlock":
            return self.unlock()
        if action.kind == "delete_file":
            return self.delete_file(p.get("path", ""))
        if action.kind == "send_file":
            return self.send_file(p.get("path", ""), p.get("to", ""))
        return ToolResult(False, "no action")

    def snapshot(self) -> dict[str, Any]:
        return {
            "payments": list(self.payments),
            "doors": list(self.doors),
            "deleted": list(self.deleted),
            "sent": list(self.sent),
            "locked": self.locked,
            "balance": self.balance,
        }
