"""MetaModelClient behaviour against a local OpenAI-compatible mock."""

from __future__ import annotations

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from onlyyou.model import MetaModelClient, Observation


class MockState:
    calls = 0
    mode = "json"
    auth = ""
    content = ""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        return

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0) or 0)
        self.rfile.read(length)
        MockState.calls += 1
        MockState.auth = self.headers.get("Authorization", "")
        if MockState.mode == "retry" and MockState.calls == 1:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"fail")
            return
        if MockState.mode == "prose" and MockState.calls == 1:
            content = "The action is pay."
        elif MockState.mode == "prose":
            content = json.dumps(
                {"kind": "pay", "params": {"payee": "electrician", "amount": 10}, "source_id": "voice:owner"}
            )
        else:
            content = json.dumps(
                {"kind": "pay", "params": {"payee": "electrician", "amount": 10}, "source_id": "voice:owner"}
            )
        body = json.dumps(
            {
                "choices": [{"message": {"content": content}}],
                "usage": {"prompt_tokens": 11, "completion_tokens": 7},
            }
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class TestMetaClient(unittest.TestCase):
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
        MockState.mode = "json"
        MockState.auth = ""
        self.client = MetaModelClient(base_url=self.base, api_key="test-key", model="mock", retries=2)

    def test_propose_parses_json_action(self):
        obs = Observation(mode="labeled", labels=[], owner_command="pay this invoice")
        action = self.client.propose(obs, "D")
        self.assertIsNotNone(action)
        self.assertEqual(action.kind, "pay")
        self.assertEqual(action.params["payee"], "electrician")
        self.assertEqual(self.client.stats["calls"], 1)
        self.assertEqual(self.client.stats["prompt_tokens"], 11)

    def test_retries_on_500(self):
        MockState.mode = "retry"
        self.client.chat([{"role": "user", "content": "ping"}])
        self.assertGreaterEqual(MockState.calls, 2)
        self.assertGreaterEqual(self.client.stats["retries"], 1)

    def test_sends_bearer_token(self):
        self.client.chat([{"role": "user", "content": "ping"}])
        self.assertEqual(MockState.auth, "Bearer test-key")

    def test_repairs_prose_answer(self):
        MockState.mode = "prose"
        obs = Observation(mode="labeled", labels=[], owner_command="pay this invoice")
        action = self.client.propose(obs, "D")
        self.assertIsNotNone(action)
        self.assertGreaterEqual(MockState.calls, 2)


if __name__ == "__main__":
    unittest.main()
