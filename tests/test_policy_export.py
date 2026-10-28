"""Signed policy snapshots: export, verify, import, tamper rejection."""

from __future__ import annotations

import json
import unittest

from onlyyou.devicekey import DeviceKey
from onlyyou.webapp import DemoService
from tools.verify_audit import verify_bundle


def canonical(bundle: dict) -> bytes:
    return json.dumps(
        {"format": bundle["format"], "issued_at": bundle["issued_at"], "rules": bundle["rules"]},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()


class TestPolicyExport(unittest.TestCase):
    def setUp(self):
        self.svc = DemoService()
        self.svc.reset()
        self.svc.set_rule_enabled({"rule_id": "R1-payee-not-contact", "enabled": False})

    def test_export_is_signed_and_reflects_state(self):
        bundle = self.svc.export_policy()
        self.assertEqual(bundle["format"], "only-you-policy/1")
        self.assertTrue(bundle["public_key"].startswith("-----BEGIN PUBLIC KEY-----"))
        self.assertTrue(DeviceKey.verify(canonical(bundle), bundle["signature"], bundle["public_key"]))
        rules = {r["id"]: r["enabled"] for r in bundle["rules"]}
        self.assertFalse(rules["R1-payee-not-contact"])

    def test_import_restores_state_and_receipts(self):
        bundle = self.svc.export_policy()
        target = DemoService()
        target.device_key = self.svc.device_key
        target.reset()
        result = target.import_policy({"bundle": bundle})
        self.assertTrue(result["ok"])
        self.assertTrue(result["receipt_ok"])
        rules = {r["id"]: r["enabled"] for r in result["state"]["rules"]}
        self.assertFalse(rules["R1-payee-not-contact"])
        receipt = result["state"]["receipts"][-1]
        self.assertEqual(receipt["action"]["kind"], "policy_import")
        self.assertEqual(receipt["verdict"]["rule"], "R7-policy-import")
        export = target.export_audit()
        self.assertTrue(verify_bundle(export)["receipts_ok"])


    def test_diff_lists_changes_without_applying(self):
        bundle = self.svc.export_policy()
        target = DemoService()
        target.device_key = self.svc.device_key
        target.reset()
        diff = target.diff_policy({"bundle": bundle})
        self.assertTrue(diff["valid"])
        self.assertFalse(diff["same"])
        self.assertEqual(len(diff["changes"]), 1)
        change = diff["changes"][0]
        self.assertEqual(change["id"], "R1-payee-not-contact")
        self.assertTrue(change["before"])
        self.assertFalse(change["after"])
        self.assertEqual(change["action"], "disable")
        rules = {r["id"]: r["enabled"] for r in target.state()["rules"]}
        self.assertTrue(rules["R1-payee-not-contact"], "diff must not apply the change")

    def test_diff_rejects_tampered_or_unknown(self):
        bundle = self.svc.export_policy()
        tampered = dict(bundle)
        tampered["rules"] = [{**r, "enabled": True} for r in bundle["rules"]]
        with self.assertRaises(ValueError):
            self.svc.diff_policy({"bundle": tampered})
        unknown = dict(bundle)
        unknown["rules"] = [{"id": "R99-unknown", "enabled": True, "description": "x"}]
        unknown["signature"] = self.svc.device_key.sign(canonical(unknown))
        with self.assertRaises(ValueError):
            self.svc.diff_policy({"bundle": unknown})

    def test_tampered_or_unknown_bundle_rejected(self):
        bundle = self.svc.export_policy()
        tampered = dict(bundle)
        tampered["rules"] = [{**r, "enabled": True} for r in bundle["rules"]]
        with self.assertRaises(ValueError):
            self.svc.import_policy({"bundle": tampered})

        unknown = dict(bundle)
        unknown["rules"] = [{"id": "R99-unknown", "enabled": True, "description": "x"}]
        unknown["signature"] = self.svc.device_key.sign(canonical(unknown))
        with self.assertRaises(ValueError):
            self.svc.import_policy({"bundle": unknown})


if __name__ == "__main__":
    unittest.main()
