"""API surface: machine-readable spec and the rendered docs page."""

from __future__ import annotations

import json
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

from onlyyou.webapp import DemoService, make_handler


class TestOpenApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(DemoService()))
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_spec_is_openapi_31_and_covers_core_paths(self):
        with urllib.request.urlopen(self.base + "/api/openapi.json", timeout=5) as resp:
            spec = json.load(resp)
        self.assertEqual(spec["openapi"], "3.1.0")
        self.assertGreaterEqual(len(spec["paths"]), 20)
        for path in ("/api/command", "/api/mandate", "/api/receipts", "/api/export", "/api/policy/diff"):
            self.assertIn(path, spec["paths"])
        self.assertIn("post", spec["paths"]["/api/command"])
        self.assertIn("summary", spec["paths"]["/api/command"]["post"])

    def test_docs_page_renders(self):
        with urllib.request.urlopen(self.base + "/docs", timeout=5) as resp:
            page = resp.read().decode()
        self.assertEqual(resp.status, 200)
        self.assertIn("ONLY YOU · API", page)
        self.assertIn("/api/openapi.json", page)
        self.assertIn("/api/command", page)
        self.assertIn("POST", page)


if __name__ == "__main__":
    unittest.main()
