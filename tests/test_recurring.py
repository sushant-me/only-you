"""Recurring mandates: the allowance resets each period."""

from __future__ import annotations

import unittest

from onlyyou.mandates import MandateLedger
from onlyyou.receipts import DEMO_SECRET
from onlyyou.webapp import DemoService
from tools.verify_audit import verify_bundle

MONTH = 30 * 24 * 3600


class TestRecurring(unittest.TestCase):
    def test_checkout_uses_period_budget(self):
        svc = DemoService()
        svc.reset()
        granted = svc.grant_mandate({
            "payees": ["electrician"], "max_amount": 5000,
            "period_seconds": MONTH, "ttl_seconds": MONTH,
        })
        mid = granted["mandate"]["id"]
        paid = svc.checkout({"id": mid, "payee": "electrician", "amount": 4500})
        self.assertTrue(paid["ok"], paid)
        mandate = next(m for m in paid["payment"]["state"]["mandates"] if m["id"] == mid)
        self.assertTrue(mandate["recurring"])
        self.assertEqual(mandate["spent_period"], 4500)
        self.assertEqual(mandate["remaining"], 500)
        self.assertIsNotNone(mandate["resets_at"])

        rejected = svc.checkout({"id": mid, "payee": "electrician", "amount": 1000})
        self.assertFalse(rejected["ok"])
        self.assertIn("remaining", rejected["reason"])

    def test_period_rollover_restores_allowance(self):
        ledger = MandateLedger(DEMO_SECRET)
        mandate = ledger.issue(
            payees=["electrician"], max_amount=100, ttl_seconds=86400,
            period_seconds=100, now=1000,
        )
        ledger.consume(mandate, 80, payee="electrician", now=1050)
        action = {"kind": "pay", "params": {"payee": "electrician", "amount": 40}}
        ok, _ = mandate.covers(action, 1050, ledger.consumed(mandate, 1050))
        self.assertFalse(ok)
        self.assertEqual(ledger.remaining(mandate, 1050), 20)
        ok, _ = mandate.covers(action, 1200, ledger.consumed(mandate, 1200))
        self.assertTrue(ok)
        self.assertEqual(ledger.remaining(mandate, 1200), 100)

    def test_invalid_period_and_export_verification(self):
        svc = DemoService()
        svc.reset()
        with self.assertRaises(ValueError):
            svc.grant_mandate({"payees": ["electrician"], "max_amount": 100, "period_seconds": -1})
        svc.grant_mandate({
            "payees": ["electrician"], "max_amount": 500,
            "period_seconds": MONTH, "ttl_seconds": MONTH,
        })
        bundle = svc.export_audit()
        self.assertTrue(verify_bundle(bundle)["mandates_ok"])


if __name__ == "__main__":
    unittest.main()
