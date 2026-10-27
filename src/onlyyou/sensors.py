"""Signed sensor envelopes.

The router trusts the signals it is given: speaker score, proximity, DOM origin,
OCR confidence. That is fine if the signals come from the sensor pipeline and
fatal if any other component can write them. This module is the missing
boundary: the sensor bus signs what it observed, and a strict router refuses to
treat unsigned signals as authoritative.

It does not stop a cloned voice (the sensor is honest; the voice is fake) and it
does not stop a compromised sensor. It stops the cheaper attack: a page, an app,
or a tool result that fabricates `speaker_score: 0.99` and expects to be obeyed.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass

from .provenance import Input


def _payload(channel: str, source_id: str, text: str, signals: dict) -> bytes:
    body = {
        "channel": channel,
        "source_id": source_id,
        "text": text,
        "signals": {k: v for k, v in signals.items() if k != "sig"},
    }
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode()


@dataclass
class SensorBus:
    secret: bytes

    def sign(self, inp: Input) -> Input:
        sig = hmac.new(
            self.secret,
            _payload(inp.channel.value, inp.source_id, inp.text, inp.signals),
            hashlib.sha256,
        ).hexdigest()
        signals = {**inp.signals, "sig": sig}
        return Input(
            channel=inp.channel,
            text=inp.text,
            source_id=inp.source_id,
            signals=signals,
            stealth=inp.stealth,
        )

    def verify(self, inp: Input) -> bool:
        sig = str(inp.signals.get("sig", ""))
        if not sig:
            return False
        expected = hmac.new(
            self.secret,
            _payload(inp.channel.value, inp.source_id, inp.text, inp.signals),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(sig, expected)
