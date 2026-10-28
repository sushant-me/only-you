"""Scheduled standing instructions: run only while a valid mandate covers them."""

from __future__ import annotations

import unittest

from onlyyou.webapp import DemoService

MONTH = 30 * 24 * 3600


class TestSchedule(unittest.TestCase):
    def setUp(self):
        self.svc = DemoService()
        self.svc.reset()
        self.svc.grant_mandate({
            "payees": ["electrician"], "max_amount": 5000,
            "period_seconds": MONTH, "ttl_seconds": MONTH,
        })
        self.mandate_id = self.svc.state()["mandates"][0]["id"]

    def test_create_and_run_pays_under_mandate(self):
        created = self.svc.create_schedule({
            "payee": "electrician", "amount": 500,
            "every_seconds": MONTH, "mandate_id": self.mandate_id,
        })
        schedule = created["schedule"]
        self.assertEqual(schedule["runs"], 0)
        self.assertGreater(schedule["next_run"], schedule["created_at"])

        result = self.svc.run_schedule({"id": schedule["id"]})
        self.assertTrue(result["ok"], result)
        self.assertTrue(result["receipt_ok"])
        self.assertEqual(result["receipt"]["verdict"]["rule"], "R8-scheduled")
        self.assertEqual(result["receipt"]["verdict"]["evidence"]["schedule_id"], schedule["id"])
        self.assertEqual(result["schedule"]["runs"], 1)
        self.assertEqual(result["schedule"]["last_run"] is not None, True)
        mandate = result["state"]["mandates"][0]
        self.assertEqual(mandate["consumed"], 500)
        self.assertEqual(mandate["remaining"], 4500)

    def test_revoked_mandate_blocks_the_run(self):
        created = self.svc.create_schedule({
            "payee": "electrician", "amount": 500,
            "every_seconds": MONTH, "mandate_id": self.mandate_id,
        })
        self.svc.revoke_all_mandates()
        before = self.svc.state()["summary"]["count"]
        result = self.svc.run_schedule({"id": created["schedule"]["id"]})
        self.assertFalse(result["ok"])
        self.assertIn("invalid", result["reason"])
        self.assertEqual(result["state"]["summary"]["count"], before)
        self.assertEqual(result["state"]["alerts"][-1]["kind"], "scheduled_payment_blocked")

    def test_invalid_schedules_rejected(self):
        with self.assertRaises(ValueError):
            self.svc.create_schedule({"payee": "electrician", "amount": 0, "mandate_id": self.mandate_id})
        with self.assertRaises(ValueError):
            self.svc.create_schedule({
                "payee": "electrician", "amount": 10,
                "every_seconds": 10, "mandate_id": self.mandate_id,
            })
        with self.assertRaises(ValueError):
            self.svc.create_schedule({"payee": "electrician", "amount": 10, "mandate_id": "nope"})
        with self.assertRaises(ValueError):
            self.svc.create_schedule({"payee": "scammer", "amount": 10, "mandate_id": self.mandate_id})

    def test_undo_refunds_scheduled_payment(self):
        created = self.svc.create_schedule({
            "payee": "electrician", "amount": 500,
            "every_seconds": MONTH, "mandate_id": self.mandate_id,
        })
        result = self.svc.run_schedule({"id": created["schedule"]["id"]})
        undo = self.svc.undo(result["receipt"]["id"])
        self.assertTrue(undo["ok"])
        self.assertEqual(undo["state"]["mandates"][0]["consumed"], 0)
        self.assertEqual(self.svc.world.balance, 50000)


if __name__ == "__main__":
    unittest.main()
