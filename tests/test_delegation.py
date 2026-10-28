"""Recursive delegation: a sub-agent's mandate can only narrow authority."""

from __future__ import annotations

import unittest

from onlyyou.webapp import DemoService
from tools.verify_audit import verify_bundle


class TestDelegation(unittest.TestCase):
    def setUp(self):
        self.svc = DemoService()
        self.svc.reset()
        self.svc.grant_mandate({"payees": ["electrician"], "max_amount": 5000})
        self.parent_id = self.svc.state()["mandates"][0]["id"]

    def test_sub_mandate_pays_and_consumes_both(self):
        sub = self.svc.grant_mandate({
            "parent_id": self.parent_id,
            "payees": ["electrician"],
            "max_amount": 1000,
            "daily_limit": 1000,
        })
        sub_id = sub["mandate"]["id"]
        self.assertEqual(sub["mandate"]["parent_id"], self.parent_id)

        result = self.svc.checkout({"id": sub_id, "payee": "electrician", "amount": 900})
        self.assertTrue(result["ok"], result)
        state = result["payment"]["state"]
        parent = next(m for m in state["mandates"] if m["id"] == self.parent_id)
        child = next(m for m in state["mandates"] if m["id"] == sub_id)
        self.assertEqual(parent["consumed"], 900)
        self.assertEqual(child["consumed"], 900)
        self.assertEqual(child["remaining"], 100)

        undo = self.svc.undo(result["payment"]["receipt"]["id"])
        self.assertTrue(undo["ok"])
        parent = next(m for m in undo["state"]["mandates"] if m["id"] == self.parent_id)
        child = next(m for m in undo["state"]["mandates"] if m["id"] == sub_id)
        self.assertEqual((parent["consumed"], child["consumed"]), (0, 0))

    def test_widening_is_rejected(self):
        with self.assertRaises(ValueError):
            self.svc.grant_mandate({
                "parent_id": self.parent_id, "payees": ["scammer"], "max_amount": 10,
            })
        with self.assertRaises(ValueError):
            self.svc.grant_mandate({"parent_id": self.parent_id, "max_amount": 9000})
        with self.assertRaises(ValueError):
            self.svc.grant_mandate({
                "parent_id": self.parent_id, "max_amount": 100, "ttl_seconds": 10 ** 7,
            })

    def test_parent_remaining_limits_child(self):
        self.svc.command({
            "speaker": "owner", "channel": "document", "text": "pay this invoice",
            "payload": "INVOICE #7781 - ELECTRICIAN - 4500",
            "invoice": {"payee": "electrician", "amount": 4500}, "confirms": True,
        })
        with self.assertRaises(ValueError):
            self.svc.grant_mandate({"parent_id": self.parent_id, "max_amount": 1000})

    def test_sub_mandate_verifies_in_audit_export(self):
        sub = self.svc.grant_mandate({
            "parent_id": self.parent_id, "payees": ["electrician"], "max_amount": 500,
        })
        bundle = self.svc.export_audit()
        ids = {m["id"] for m in bundle["mandates"]}
        self.assertIn(sub["mandate"]["id"], ids)
        self.assertTrue(verify_bundle(bundle)["mandates_ok"])


if __name__ == "__main__":
    unittest.main()
