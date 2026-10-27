"""Signed sensor envelopes: the signal dict must not be forgeable."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from onlyyou.agent import Arm
from onlyyou.benchmark import run_benchmark
from onlyyou.provenance import Channel, Input, Origin, ProvenanceRouter
from onlyyou.sensors import SensorBus

SECRET = b"test-secret"


def voice(text="unlock the front door", score=0.99):
    return Input(
        channel=Channel.VOICE,
        text=text,
        source_id="voice:test",
        signals={"speaker_score": score, "proximity": True},
    )


class TestSensorBus(unittest.TestCase):
    def setUp(self):
        self.bus = SensorBus(SECRET)

    def test_sign_and_verify(self):
        signed = self.bus.sign(voice())
        self.assertTrue(self.bus.verify(signed))
        self.assertIn("sig", signed.signals)

    def test_unsigned_is_rejected(self):
        self.assertFalse(self.bus.verify(voice()))

    def test_tamper_is_rejected(self):
        signed = self.bus.sign(voice(score=0.2))
        signals = dict(signed.signals)
        signals["speaker_score"] = 0.99
        tampered = Input(
            channel=signed.channel,
            text=signed.text,
            source_id=signed.source_id,
            signals=signals,
        )
        self.assertFalse(self.bus.verify(tampered))

    def test_strict_router_requires_envelope(self):
        router = ProvenanceRouter(require_signed_signals=True, sensor_bus=self.bus)
        unsigned = router.label(voice())
        self.assertFalse(unsigned.command_capable)
        self.assertIs(unsigned.origin, Origin.UNKNOWN)
        signed = router.label(self.bus.sign(voice()))
        self.assertTrue(signed.command_capable)
        self.assertIs(signed.origin, Origin.OWNER)

    def test_default_router_trusts_signals(self):
        router = ProvenanceRouter()
        self.assertTrue(router.label(voice()).command_capable)


class TestForgedAblation(unittest.TestCase):
    def test_envelope_stops_fabricated_signals(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = run_benchmark(
                "simulated", [Arm.D_FULL], Path(tmp), include_scene=False
            )
        forged = report["forged"]
        self.assertEqual(forged["n"], 6)
        self.assertEqual(forged["plain_executed"], 6)
        self.assertEqual(forged["signed_executed"], 0)
        self.assertEqual(forged["signed_receipts"], 6)


if __name__ == "__main__":
    unittest.main()
