"""Public receipt verification page and JSON endpoint."""

from __future__ import annotations

import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from onlyyou.webapp import DemoService, make_handler


class TestVerifyPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = DemoService()
        cls.service.grant_mandate({"payees": ["electrician"], "max_amount": 5000})
        result = cls.service.command({
            "speaker": "owner", "channel": "document", "text": "pay this invoice",
            "payload": "INVOICE #7781 - ELECTRICIAN - 4500",
            "invoice": {"payee": "electrician", "amount": 4500}, "confirms": True,
        })
        cls.receipt = result["receipt"]
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(cls.service))
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_page_shows_valid_rule_and_chain(self):
        with urllib.request.urlopen(self.base + f"/verify/{self.receipt['id']}", timeout=5) as resp:
            page = resp.read().decode()
        self.assertEqual(resp.status, 200)
        self.assertIn("R6-mandate", page)
        self.assertIn("VALID", page)
        self.assertIn("chain</th><td>OK", page)
        self.assertIn(self.receipt["id"], page)

    def test_json_endpoint_and_unknown_id(self):
        with urllib.request.urlopen(self.base + f"/api/receipt/{self.receipt['id']}", timeout=5) as resp:
            body = resp.read().decode()
        self.assertIn('"signature_ok": true', body)
        self.assertIn('"chain_ok": true', body)
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(self.base + "/verify/does-not-exist", timeout=5)
        self.assertEqual(ctx.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
