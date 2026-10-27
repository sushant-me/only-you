"""Ed25519 device keys and merchant-side mandate verification."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from onlyyou.devicekey import DeviceKey
from onlyyou.mandates import MandateLedger, merchant_verify

SECRET = b"test-ledger-secret"
ACTION = {"kind": "pay", "params": {"payee": "electrician", "amount": 4500}}


class TestDeviceKey(unittest.TestCase):
    def test_sign_and_verify(self):
        with tempfile.TemporaryDirectory() as td:
            key = DeviceKey.create(td)
            sig = key.sign(b"hello")
            self.assertTrue(sig.startswith("ed25519:"))
            self.assertTrue(DeviceKey.verify(b"hello", sig, key.public_pem))
            self.assertFalse(DeviceKey.verify(b"hello!", sig, key.public_pem))

    def test_merchant_accepts_valid_mandate(self):
        with tempfile.TemporaryDirectory() as td:
            key = DeviceKey.create(td)
            ledger = MandateLedger(SECRET, device_key=key)
            m = ledger.issue(payees=["electrician"], max_amount=5000, ttl_seconds=3600)
            ok, why = merchant_verify(m.to_dict(), ACTION, key.public_pem, now=m.issued_at + 1)
            self.assertTrue(ok, why)
            self.assertIn("mandate", why)

    def test_merchant_rejects_over_cap(self):
        with tempfile.TemporaryDirectory() as td:
            key = DeviceKey.create(td)
            ledger = MandateLedger(SECRET, device_key=key)
            m = ledger.issue(payees=["electrician"], max_amount=1000, ttl_seconds=3600)
            ok, why = merchant_verify(m.to_dict(), ACTION, key.public_pem, now=m.issued_at + 1)
            self.assertFalse(ok)
            self.assertIn("budget", why)

    def test_merchant_rejects_tampered_mandate(self):
        with tempfile.TemporaryDirectory() as td:
            key = DeviceKey.create(td)
            ledger = MandateLedger(SECRET, device_key=key)
            d = ledger.issue(payees=["electrician"], max_amount=5000, ttl_seconds=3600).to_dict()
            d["max_amount"] = 999999
            ok, why = merchant_verify(d, ACTION, key.public_pem)
            self.assertFalse(ok)
            self.assertIn("signature", why)

    def test_merchant_rejects_wrong_key(self):
        with tempfile.TemporaryDirectory() as td:
            key = DeviceKey.create(td)
            other = DeviceKey.create(Path(td) / "other")
            ledger = MandateLedger(SECRET, device_key=key)
            m = ledger.issue(payees=["electrician"], max_amount=5000, ttl_seconds=3600)
            ok, _ = merchant_verify(m.to_dict(), ACTION, other.public_pem, now=m.issued_at + 1)
            self.assertFalse(ok)

    def test_merchant_rejects_expired(self):
        with tempfile.TemporaryDirectory() as td:
            key = DeviceKey.create(td)
            ledger = MandateLedger(SECRET, device_key=key)
            m = ledger.issue(payees=["electrician"], max_amount=5000, ttl_seconds=60)
            ok, why = merchant_verify(m.to_dict(), ACTION, key.public_pem, now=m.expires_at + 1)
            self.assertFalse(ok)
            self.assertIn("expired", why)


if __name__ == "__main__":
    unittest.main()
