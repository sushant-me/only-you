"""Mandates: delegation, not just permission.

A constitution says what the agent may *never* do. A mandate says what the owner
has *temporarily authorised* — a scoped, expiring, signed capability:

    "You may pay the electrician up to 5,000 until Friday."

That distinction is the difference between an assistant that interrupts you for
every routine action and one you can actually delegate to. It is also the thing
a merchant needs in order to trust an agent-initiated payment: not a prompt, a
verifiable authorisation from the principal.

Design notes
  * A mandate is signed with the device key (HMAC here; passkey/SEK in a product).
  * It is scoped (action kind), bounded (payee allow-list, amount cap), and
    time-limited.
  * It can be revoked; verification checks signature + expiry + revocation.
  * The agent still runs provenance first: a mandate authorises *actions*, it
    never turns untrusted content into an instruction.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from datetime import datetime, timezone
from dataclasses import asdict, dataclass, field
from typing import Any

from .devicekey import DeviceKey


@dataclass
class Mandate:
    id: str
    principal: str
    scope: str  # "pay" | "unlock" | ... (the action kind it authorises)
    payees: list[str] = field(default_factory=list)
    max_amount: int = 0
    issued_at: float = 0.0
    expires_at: float = 0.0
    nonce: str = ""
    note: str = ""
    # Optional sub-limits, signed with the rest of the mandate.
    payee_limits: dict[str, int] = field(default_factory=dict)
    daily_limit: int = 0
    signature: str = ""

    def payload(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("signature", None)
        return d

    def canonical(self) -> str:
        return json.dumps(self.payload(), sort_keys=True, separators=(",", ":"))

    def covers(
        self,
        action: dict[str, Any],
        now: float | None = None,
        spent: int = 0,
        spent_payee: int = 0,
        spent_today: int = 0,
    ) -> tuple[bool, str]:
        """Does this mandate authorise the given action, given prior spend?"""
        now = time.time() if now is None else now
        if now > self.expires_at:
            return False, "mandate expired"
        kind = str(action.get("kind", ""))
        if kind != self.scope:
            return False, f"scope mismatch: mandate authorises {self.scope}, action is {kind}"
        if kind == "pay":
            params = action.get("params") or {}
            payee = str(params.get("payee", "")).lower()
            amount = int(params.get("amount", 0))
            if payee not in {p.lower() for p in self.payees}:
                return False, f"payee {payee!r} not in mandate"
            remaining = self.max_amount - spent
            if amount > remaining:
                return False, (
                    f"amount {amount} exceeds remaining mandate budget {remaining} "
                    f"(cap {self.max_amount}, spent {spent})"
                )
            payee_limit = self.payee_limits.get(payee)
            if payee_limit is not None and amount > payee_limit - spent_payee:
                return False, (
                    f"amount {amount} exceeds @{payee} sub-limit {payee_limit} "
                    f"(spent {spent_payee})"
                )
            if self.daily_limit and amount > self.daily_limit - spent_today:
                return False, (
                    f"amount {amount} exceeds daily sub-limit {self.daily_limit} "
                    f"(spent today {spent_today})"
                )
        return True, "within mandate"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MandateLedger:
    """Issue, verify, revoke and match mandates."""

    def __init__(
        self,
        secret: bytes,
        max_ttl_seconds: int = 7 * 24 * 3600,
        device_key: DeviceKey | None = None,
    ) -> None:
        self.secret = secret
        self.max_ttl_seconds = max_ttl_seconds
        self.device_key = device_key
        self.mandates: list[Mandate] = []
        self.revoked: set[str] = set()
        self.spent: dict[str, int] = {}
        self.spent_payee: dict[str, int] = {}
        self.spent_by_day: dict[str, dict[str, int]] = {}

    @property
    def public_key_pem(self) -> str:
        return self.device_key.public_pem if self.device_key else ""

    # -- signing -----------------------------------------------------------
    def _sign(self, payload: dict[str, Any]) -> str:
        msg = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hmac.new(self.secret, msg, hashlib.sha256).hexdigest()

    # -- lifecycle ---------------------------------------------------------
    def issue(
        self,
        scope: str = "pay",
        payees: list[str] | None = None,
        max_amount: int = 0,
        ttl_seconds: int = 24 * 3600,
        principal: str = "owner",
        note: str = "",
        payee_limits: dict[str, int] | None = None,
        daily_limit: int = 0,
        now: float | None = None,
    ) -> Mandate:
        now = time.time() if now is None else now
        ttl = max(1, min(int(ttl_seconds), self.max_ttl_seconds))
        m = Mandate(
            id=secrets.token_hex(6),
            principal=principal,
            scope=scope,
            payees=[p.lower() for p in (payees or [])],
            max_amount=int(max_amount),
            issued_at=now,
            expires_at=now + ttl,
            nonce=secrets.token_hex(8),
            note=note,
            payee_limits={str(k).lower(): int(v) for k, v in (payee_limits or {}).items()},
            daily_limit=int(daily_limit),
        )
        if self.device_key is not None:
            m.signature = self.device_key.sign(m.canonical().encode())
        else:
            m.signature = self._sign(m.payload())
        self.mandates.append(m)
        return m

    def verify(self, mandate: Mandate, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        if mandate.id in self.revoked:
            return False
        if now > mandate.expires_at:
            return False
        if mandate.signature.startswith("ed25519:"):
            if self.device_key is None:
                return False
            return DeviceKey.verify(
                mandate.canonical().encode(), mandate.signature, self.device_key.public_pem
            )
        return hmac.compare_digest(mandate.signature, self._sign(mandate.payload()))

    def revoke(self, mandate_id: str) -> bool:
        if any(m.id == mandate_id for m in self.mandates):
            self.revoked.add(mandate_id)
            return True
        return False

    def find_covering(
        self, action: dict[str, Any], now: float | None = None
    ) -> tuple[Mandate | None, str]:
        for m in self.mandates:
            if not self.verify(m, now):
                continue
            params = action.get("params") or {}
            payee = str(params.get("payee", "")).lower() if action.get("kind") == "pay" else ""
            ok, why = m.covers(
                action,
                now,
                self.spent.get(m.id, 0),
                self.consumed_payee(m, payee),
                self.consumed_today(m, now),
            )
            if ok:
                return m, why
        return None, "no covering mandate"

    # -- spend tracking (kept outside the signed payload) -------------------
    def remaining(self, mandate: Mandate) -> int:
        return max(0, mandate.max_amount - self.spent.get(mandate.id, 0))

    @staticmethod
    def _day(now: float | None = None) -> str:
        return datetime.fromtimestamp(now or time.time(), timezone.utc).date().isoformat()

    def consumed_payee(self, mandate: Mandate, payee: str) -> int:
        return self.spent_payee.get(f"{mandate.id}|{payee.lower().lstrip('@')}", 0)

    def consumed_today(self, mandate: Mandate, now: float | None = None) -> int:
        return self.spent_by_day.get(mandate.id, {}).get(self._day(now), 0)

    def consume(
        self, mandate: Mandate, amount: int, payee: str = "", now: float | None = None
    ) -> None:
        amount = int(amount)
        self.spent[mandate.id] = self.spent.get(mandate.id, 0) + amount
        if payee:
            key = f"{mandate.id}|{payee.lower().lstrip('@')}"
            self.spent_payee[key] = self.spent_payee.get(key, 0) + amount
        day = self._day(now)
        bucket = self.spent_by_day.setdefault(mandate.id, {})
        bucket[day] = bucket.get(day, 0) + amount

    def refund(
        self, mandate: Mandate, amount: int, payee: str = "", now: float | None = None
    ) -> None:
        """Undo an executed spend, restoring total, per-payee and daily budgets."""
        amount = int(amount)
        self.spent[mandate.id] = max(0, self.spent.get(mandate.id, 0) - amount)
        if payee:
            key = f"{mandate.id}|{payee.lower().lstrip('@')}"
            self.spent_payee[key] = max(0, self.spent_payee.get(key, 0) - amount)
        day = self._day(now)
        bucket = self.spent_by_day.setdefault(mandate.id, {})
        bucket[day] = max(0, bucket.get(day, 0) - amount)

    # -- merchant-side check (the commerce extension) ----------------------
    def verify_for_merchant(
        self, mandate: Mandate, action: dict[str, Any], now: float | None = None
    ) -> bool:
        """What a merchant would run before accepting an agent payment.

        The merchant does not need to trust the agent or the platform: it checks
        the principal's signature, the scope, the payee and the cap.
        """
        return self.verify(mandate, now) and mandate.covers(action, now)[0]

    # -- reporting ---------------------------------------------------------
    def to_dicts(self, now: float | None = None) -> list[dict[str, Any]]:
        return [
            {
                **m.to_dict(),
                "valid": self.verify(m, now),
                "revoked": m.id in self.revoked,
                "consumed": self.spent.get(m.id, 0),
                "remaining": self.remaining(m),
                "spent_today": self.consumed_today(m),
                "remaining_today": (
                    max(0, m.daily_limit - self.consumed_today(m)) if m.daily_limit else None
                ),
            }
            for m in self.mandates
        ]


def merchant_verify(
    mandate: dict[str, Any],
    action: dict[str, Any],
    public_pem: str,
    now: float | None = None,
) -> tuple[bool, str]:
    """Offline check a merchant runs before accepting an agent-initiated payment.

    Inputs are plain JSON (what the agent presents at checkout) and the device
    public key. No shared secret, no call to the agent or platform.
    """
    m = Mandate(
        id=str(mandate.get("id", "")),
        principal=str(mandate.get("principal", "")),
        scope=str(mandate.get("scope", "")),
        payees=[str(p).lower() for p in mandate.get("payees", [])],
        max_amount=int(mandate.get("max_amount", 0)),
        issued_at=float(mandate.get("issued_at", 0)),
        expires_at=float(mandate.get("expires_at", 0)),
        nonce=str(mandate.get("nonce", "")),
        note=str(mandate.get("note", "")),
        payee_limits={str(k).lower(): int(v) for k, v in (mandate.get("payee_limits") or {}).items()},
        daily_limit=int(mandate.get("daily_limit", 0) or 0),
        signature=str(mandate.get("signature", "")),
    )
    if not DeviceKey.verify(m.canonical().encode(), m.signature, public_pem):
        return False, "signature invalid"
    ok, why = m.covers(action, now)
    return ok, why
