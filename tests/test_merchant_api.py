"""Merchant verification endpoint: offline Ed25519 check of a mandate."""

from __future__ import annotations

import unittest

from onlyyou.webapp import DemoService


class TestMerchantApi(unittest.TestCase):
    def setUp(self):
        self.service = DemoService()
        self.service.reset()

    def test_valid_mandate_verifies(self):
        mandate = self.service.grant_mandate({"payees": ["electrician"], "max_amount": 5000})["mandate"]
        result = self.service.merchant_verify(
            {"id": mandate["id"], "action": {"kind": "pay", "params": {"payee": "electrician", "amount": 4500}}}
        )
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["algorithm"], "ed25519")

    def test_over_cap_rejected(self):
        mandate = self.service.grant_mandate({"payees": ["electrician"], "max_amount": 1000})["mandate"]
        result = self.service.merchant_verify(
            {"id": mandate["id"], "action": {"kind": "pay", "params": {"payee": "electrician", "amount": 5000}}}
        )
        self.assertFalse(result["ok"])
        self.assertIn("budget", result["reason"])

    def test_unknown_mandate_rejected(self):
        self.assertFalse(self.service.merchant_verify({"id": "nope"})["ok"])


if __name__ == "__main__":
    unittest.main()
