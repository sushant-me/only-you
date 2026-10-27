"""Integration: the real-model and open-weights benchmark paths, against a mock endpoint.

This is the test that matters before the API key arrives: it proves that
`run_benchmark("meta")` and `run_benchmark("open")` construct the client, make
calls, and write a report with model metadata — so the only unknown left is the
credential, not the plumbing.
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from onlyyou.agent import Arm
from onlyyou.benchmark import run_benchmark


class MockState:
    calls = 0


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        return

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0) or 0)
        self.rfile.read(length)
        MockState.calls += 1
        content = json.dumps(
            {"kind": "pay", "params": {"payee": "attacker0", "amount": 10}, "source_id": "mock"}
        )
        body = json.dumps(
            {"choices": [{"message": {"content": content}}], "usage": {"prompt_tokens": 5, "completion_tokens": 3}}
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class TestBenchModes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}/v1"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        MockState.calls = 0
        self.saved = {k: os.environ.get(k) for k in ("META_API_BASE", "META_API_KEY", "MUSE_MODEL", "OPEN_WEIGHTS_BASE", "OPEN_WEIGHTS_KEY", "OPEN_WEIGHTS_MODEL")}

    def tearDown(self):
        for k, v in self.saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_meta_mode_writes_report(self):
        os.environ["META_API_BASE"] = self.base
        os.environ["META_API_KEY"] = "test-key"
        os.environ["MUSE_MODEL"] = "mock-spark"
        with tempfile.TemporaryDirectory() as td:
            report = run_benchmark("meta", [Arm.A_UNDEFENDED], Path(td), limit=1, include_scene=False)
            self.assertEqual(report["mode"], "meta")
            self.assertEqual(report["model"], "mock-spark")
            self.assertGreater(report["model_info"]["stats"]["calls"], 0)
            self.assertTrue((Path(td) / "benchmark.json").exists())
            self.assertIn("latency", report)
        self.assertGreater(MockState.calls, 0)

    def test_open_weights_mode_writes_report(self):
        os.environ["OPEN_WEIGHTS_BASE"] = self.base
        os.environ["OPEN_WEIGHTS_KEY"] = "test-key"
        os.environ["OPEN_WEIGHTS_MODEL"] = "muse-glimmer-mock"
        with tempfile.TemporaryDirectory() as td:
            report = run_benchmark("open", [Arm.A_UNDEFENDED], Path(td), limit=1, include_scene=False)
            self.assertEqual(report["mode"], "open")
            self.assertEqual(report["model"], "muse-glimmer-mock")
            self.assertGreater(report["model_info"]["stats"]["calls"], 0)


if __name__ == "__main__":
    unittest.main()
