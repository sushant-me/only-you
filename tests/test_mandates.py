"""Tests for delegation mandates (scoped, expiring, signed authority)."""

from __future__ import annotations

import time
import unittest

from onlyyou.mandates import MandateLedger


class TestMandates(unittest.TestCase):
    def setUp(self):
        self.ledger = MandateLedger(b"secret")

    def _pay(self, payee="electrician", amount=4500):
        return {"kind": "pay", "params": {"payee": payee, "amount": amount}}

    def test_issue_and_verify(self):
        m = self.ledger.issue(payees=["electrician"], max_amount=5000)
        self.assertTrue(self.ledger.verify(m))
        self.assertTrue(m.signature)

    def test_tamper_breaks_signature(self):
        m = self.ledger.issue(payees=["electrician"], max_amount=5000)
        m.max_amount = 50000
        self.assertFalse(self.ledger.verify(m))

    def test_expiry(self):
        m = self.ledger.issue(payees=["electrician"], max_amount=5000, ttl_seconds=10, now=time.time() - 100)
        self.assertFalse(self.ledger.verify(m))

    def test_cover_rules(self):
        m = self.ledger.issue(payees=["electrician"], max_amount=5000)
        self.assertTrue(m.covers(self._pay())[0])
        self.assertFalse(m.covers(self._pay(amount=6000))[0])  # over cap
        self.assertFalse(m.covers(self._pay(payee="attacker0"))[0])  # wrong payee
        self.assertFalse(m.covers({"kind": "unlock", "params": {}})[0])  # wrong scope

    def test_find_covering(self):
        self.ledger.issue(payees=["electrician"], max_amount=5000)
        found, why = self.ledger.find_covering(self._pay())
        self.assertIsNotNone(found)
        self.assertIn("within mandate", why)
        none, _ = self.ledger.find_covering(self._pay(payee="attacker0"))
        self.assertIsNone(none)

    def test_revoke(self):
        m = self.ledger.issue(payees=["electrician"], max_amount=5000)
        self.assertTrue(self.ledger.revoke(m.id))
        self.assertFalse(self.ledger.verify(m))
        self.assertIsNone(self.ledger.find_covering(self._pay())[0])

    def test_merchant_verification(self):
        m = self.ledger.issue(payees=["electrician"], max_amount=5000)
        self.assertTrue(self.ledger.verify_for_merchant(m, self._pay()))
        self.assertFalse(self.ledger.verify_for_merchant(m, self._pay(amount=9000)))

    def test_cumulative_spend_and_signature_stability(self):
        m = self.ledger.issue(payees=["electrician"], max_amount=5000)
        self.ledger.consume(m, 4500)
        # Consuming does not touch the signed payload.
        self.assertTrue(self.ledger.verify(m))
        self.assertEqual(self.ledger.remaining(m), 500)
        ok, why = m.covers(self._pay(amount=600), None, self.ledger.spent[m.id])
        self.assertFalse(ok)
        self.assertIn("remaining", why)
        self.assertIsNone(self.ledger.find_covering(self._pay(amount=600))[0])
        self.assertIsNotNone(self.ledger.find_covering(self._pay(amount=400))[0])

    def test_ttl_is_clamped(self):
        m = self.ledger.issue(payees=["electrician"], max_amount=1, ttl_seconds=10**9)
        self.assertLessEqual(m.expires_at - m.issued_at, self.ledger.max_ttl_seconds)


if __name__ == "__main__":
    unittest.main()
