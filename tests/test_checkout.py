"""Merchant checkout: independent verification, budget enforcement, then payment."""

from __future__ import annotations

import unittest

from onlyyou.webapp import DemoService


class TestCheckout(unittest.TestCase):
    def setUp(self):
        self.svc = DemoService()
        self.svc.grant_mandate({"payees": ["electrician"], "max_amount": 5000})
        self.mandate_id = self.svc.state()["mandates"][0]["id"]

    def test_checkout_verifies_and_pays(self):
        result = self.svc.checkout({"id": self.mandate_id, "payee": "electrician", "amount": 4500})
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["stage"], "paid")
        self.assertTrue(result["merchant_verified"])
        self.assertEqual(result["payment"]["outcome"], "executed")
        self.assertEqual(result["mandate"]["remaining"], 500)
        self.assertTrue(result["payment"]["receipt_ok"])

    def test_checkout_rejects_over_remaining_budget(self):
        self.svc.checkout({"id": self.mandate_id, "payee": "electrician", "amount": 4500})
        result = self.svc.checkout({"id": self.mandate_id, "payee": "electrician", "amount": 1000})
        self.assertFalse(result["ok"])
        self.assertEqual(result["stage"], "merchant")
        self.assertIn("remaining", result["reason"])

    def test_checkout_rejects_revoked_mandate(self):
        self.svc.revoke_all_mandates()
        result = self.svc.checkout({"id": self.mandate_id, "payee": "electrician", "amount": 100})
        self.assertFalse(result["ok"])
        self.assertIn("invalid", result["reason"])

    def test_checkout_rejects_unknown_mandate(self):
        result = self.svc.checkout({"id": "missing", "amount": 10})
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "mandate not found")


if __name__ == "__main__":
    unittest.main()
