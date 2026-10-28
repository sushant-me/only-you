"""Operational alerts: state, webhook delivery."""

from __future__ import annotations

import json
import os
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from onlyyou.webapp import DemoService

RECEIVED: list[dict] = []


class FailingHandler(BaseHTTPRequestHandler):
    attempts = 0

    def log_message(self, *args):
        return

    def do_POST(self):  # noqa: N802
        FailingHandler.attempts += 1
        length = int(self.headers.get("Content-Length", 0) or 0)
        self.rfile.read(length)
        if FailingHandler.attempts <= FailingHandler.fail_first:
            self.send_response(500)
            self.end_headers()
        else:
            self.send_response(204)
            self.end_headers()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        return

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0) or 0)
        RECEIVED.append(json.loads(self.rfile.read(length) or b"{}"))
        self.send_response(204)
        self.end_headers()


class TestAlerts(unittest.TestCase):
    def setUp(self):
        self.svc = DemoService()
        self.svc.reset()
        self.saved = os.environ.get("ONLYYOU_WEBHOOK_URL")
        os.environ.pop("ONLYYOU_WEBHOOK_URL", None)

    def tearDown(self):
        if self.saved is None:
            os.environ.pop("ONLYYOU_WEBHOOK_URL", None)
        else:
            os.environ["ONLYYOU_WEBHOOK_URL"] = self.saved

    def test_policy_change_alert_in_state(self):
        self.svc.set_rule_enabled({"rule_id": "R2-payment-over-limit", "enabled": False})
        alerts = self.svc.state()["alerts"]
        self.assertEqual(alerts[-1]["kind"], "policy_change")
        self.assertIn("R2-payment-over-limit", alerts[-1]["message"])

    def test_revoke_all_alert(self):
        self.svc.grant_mandate({"payees": ["electrician"], "max_amount": 100})
        self.svc.revoke_all_mandates()
        self.assertEqual(self.svc.state()["alerts"][-1]["kind"], "mandates_revoked")

    def test_transient_failures_are_retried(self):
        FailingHandler.attempts = 0
        FailingHandler.fail_first = 2
        server = ThreadingHTTPServer(("127.0.0.1", 0), FailingHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        os.environ["ONLYYOU_WEBHOOK_URL"] = f"http://127.0.0.1:{server.server_address[1]}/hook"
        os.environ["ONLYYOU_WEBHOOK_RETRIES"] = "4"
        os.environ["ONLYYOU_WEBHOOK_DELAY"] = "0.02"
        try:
            self.svc.set_rule_enabled({"rule_id": "R3-unlock-requires-confirmation", "enabled": False})
            deadline = time.time() + 5
            while time.time() < deadline:
                if self.svc.state()["webhook"]["delivered"] == 1:
                    break
                time.sleep(0.05)
        finally:
            server.shutdown()
            os.environ.pop("ONLYYOU_WEBHOOK_RETRIES", None)
            os.environ.pop("ONLYYOU_WEBHOOK_DELAY", None)
        webhook = self.svc.state()["webhook"]
        self.assertEqual(webhook["delivered"], 1, webhook)
        self.assertEqual(webhook["failed"], 0, webhook)
        alert = self.svc.state()["alerts"][-1]
        self.assertEqual(alert["delivery"]["status"], "delivered")
        self.assertEqual(alert["delivery"]["attempts"], 3)

    def test_permanent_failure_is_logged(self):
        FailingHandler.attempts = 0
        FailingHandler.fail_first = 10
        server = ThreadingHTTPServer(("127.0.0.1", 0), FailingHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        os.environ["ONLYYOU_WEBHOOK_URL"] = f"http://127.0.0.1:{server.server_address[1]}/hook"
        os.environ["ONLYYOU_WEBHOOK_RETRIES"] = "2"
        os.environ["ONLYYOU_WEBHOOK_DELAY"] = "0.01"
        try:
            self.svc.set_rule_enabled({"rule_id": "R2-payment-over-limit", "enabled": False})
            deadline = time.time() + 5
            while time.time() < deadline:
                if self.svc.state()["webhook"]["failed"] == 1:
                    break
                time.sleep(0.05)
        finally:
            server.shutdown()
            os.environ.pop("ONLYYOU_WEBHOOK_RETRIES", None)
            os.environ.pop("ONLYYOU_WEBHOOK_DELAY", None)
        webhook = self.svc.state()["webhook"]
        self.assertEqual(webhook["failed"], 1, webhook)
        self.assertEqual(webhook["delivered"], 0, webhook)

    def test_webhook_delivery(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        RECEIVED.clear()
        os.environ["ONLYYOU_WEBHOOK_URL"] = f"http://127.0.0.1:{server.server_address[1]}/hook"
        try:
            self.svc.set_rule_enabled({"rule_id": "R3-unlock-requires-confirmation", "enabled": False})
            deadline = time.time() + 5
            while time.time() < deadline and not RECEIVED:
                time.sleep(0.05)
        finally:
            server.shutdown()
        self.assertTrue(RECEIVED, "webhook was not called")
        self.assertEqual(RECEIVED[0]["kind"], "policy_change")
        self.assertEqual(RECEIVED[0]["data"]["rule_id"], "R3-unlock-requires-confirmation")


if __name__ == "__main__":
    unittest.main()
