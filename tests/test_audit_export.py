"""Signed audit export: bundle structure, offline verification, tamper detection."""

from __future__ import annotations

import copy
import unittest

from onlyyou.webapp import DemoService
from tools.verify_audit import verify_bundle


def _paid_service() -> DemoService:
    svc = DemoService()
    svc.grant_mandate({"payees": ["electrician"], "max_amount": 5000})
    svc.command({
        "speaker": "owner", "channel": "document", "text": "pay this invoice",
        "payload": "INVOICE #7781 - ELECTRICIAN - 4500",
        "invoice": {"payee": "electrician", "amount": 4500}, "confirms": True,
    })
    return svc


class TestAuditExport(unittest.TestCase):
    def test_bundle_verifies_offline(self):
        bundle = _paid_service().export_audit()
        self.assertEqual(bundle["format"], "only-you-audit/1")
        self.assertTrue(bundle["chain"]["ok"])
        self.assertEqual(len(bundle["receipts"]), 1)
        self.assertEqual(len(bundle["mandates"]), 1)
        self.assertTrue(bundle["device_public_key"].startswith("-----BEGIN PUBLIC KEY-----"))

        result = verify_bundle(bundle)
        self.assertTrue(result["receipts_ok"], result)
        self.assertTrue(result["mandates_ok"], result)
        self.assertTrue(result["bundle_chain_ok"])
        self.assertEqual(result["chain_head"], bundle["chain"]["head"])

    def test_tampered_receipt_fails(self):
        bundle = _paid_service().export_audit()
        tampered = copy.deepcopy(bundle)
        tampered["receipts"][0]["action"]["params"]["amount"] = 1
        result = verify_bundle(tampered)
        self.assertFalse(result["receipts_ok"])
        self.assertIn("signature", [e["error"] for e in result["receipt_errors"]])

    def test_tampered_mandate_fails(self):
        bundle = _paid_service().export_audit()
        tampered = copy.deepcopy(bundle)
        tampered["mandates"][0]["max_amount"] = 999999
        result = verify_bundle(tampered)
        self.assertFalse(result["mandates_ok"])


if __name__ == "__main__":
    unittest.main()
