"""Signed payee and daily sub-limits on top of the mandate cap."""

from __future__ import annotations

import unittest

from onlyyou.webapp import DemoService


class TestSubLimits(unittest.TestCase):
    def test_payee_sublimit_rejected_then_within(self):
        svc = DemoService()
        svc.grant_mandate({
            "payees": ["electrician"], "max_amount": 5000,
            "payee_limits": {"electrician": 1000},
        })
        mid = svc.state()["mandates"][0]["id"]
        rejected = svc.checkout({"id": mid, "payee": "electrician", "amount": 1500})
        self.assertFalse(rejected["ok"])
        self.assertIn("sub-limit", rejected["reason"])
        accepted = svc.checkout({"id": mid, "payee": "electrician", "amount": 900})
        self.assertTrue(accepted["ok"], accepted)
        self.assertEqual(accepted["mandate"]["remaining"], 4100)

    def test_daily_sublimit(self):
        svc = DemoService()
        svc.grant_mandate({"payees": ["electrician"], "max_amount": 5000, "daily_limit": 1000})
        mid = svc.state()["mandates"][0]["id"]
        first = svc.checkout({"id": mid, "payee": "electrician", "amount": 800})
        self.assertTrue(first["ok"], first)
        second = svc.checkout({"id": mid, "payee": "electrician", "amount": 400})
        self.assertFalse(second["ok"])
        self.assertIn("daily sub-limit", second["reason"])

    def test_undo_restores_daily_and_payee_usage(self):
        svc = DemoService()
        svc.grant_mandate({
            "payees": ["electrician"], "max_amount": 5000,
            "payee_limits": {"electrician": 1000}, "daily_limit": 1000,
        })
        mid = svc.state()["mandates"][0]["id"]
        paid = svc.checkout({"id": mid, "payee": "electrician", "amount": 900})
        self.assertTrue(paid["ok"])
        receipt_id = paid["payment"]["receipt"]["id"]
        undo = svc.undo(receipt_id)
        self.assertTrue(undo["ok"])
        mandate = next(m for m in undo["state"]["mandates"] if m["id"] == mid)
        self.assertEqual(mandate["consumed"], 0)
        self.assertEqual(mandate["spent_today"], 0)

    def test_invalid_sublimits_rejected(self):
        svc = DemoService()
        with self.assertRaises(ValueError):
            svc.grant_mandate({"payees": ["electrician"], "max_amount": 100, "daily_limit": -1})
        with self.assertRaises(ValueError):
            svc.grant_mandate({"payees": ["electrician"], "max_amount": 100, "payee_limits": "nope"})


if __name__ == "__main__":
    unittest.main()
