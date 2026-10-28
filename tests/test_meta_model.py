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

        # Frontier adapter resolves provider credentials without touching the gate.
        import os

        from onlyyou.frontier import FrontierModel

        saved = {k: os.environ.pop(k, None) for k in (
            "FRONTIER_API_KEY", "FRONTIER_API_BASE", "FRONTIER_MODEL", "FRONTIER_PROVIDER",
            "OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_API_BASE",
        )}
        try:
            os.environ["OPENAI_API_KEY"] = "k"
            os.environ["OPENAI_MODEL"] = "gpt-test"
            spec = FrontierModel.resolve()
            self.assertEqual(spec["provider"], "openai")
            self.assertEqual(spec["model"], "gpt-test")
            self.assertEqual(spec["base"], "https://api.openai.com/v1")
            os.environ["FRONTIER_API_KEY"] = "explicit"
            os.environ["FRONTIER_API_BASE"] = "http://localhost:11434/v1"
            os.environ["FRONTIER_MODEL"] = "local-model"
            os.environ["FRONTIER_PROVIDER"] = "ollama"
            explicit = FrontierModel.resolve()
            self.assertEqual(explicit["provider"], "ollama")
            self.assertEqual(explicit["model"], "local-model")
            self.assertEqual(explicit["base"], "http://localhost:11434/v1")
        finally:
            for key in (
                "FRONTIER_API_KEY", "FRONTIER_API_BASE", "FRONTIER_MODEL", "FRONTIER_PROVIDER",
                "OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_API_BASE",
            ):
                os.environ.pop(key, None)
            for key, value in saved.items():
                if value is not None:
                    os.environ[key] = value

        # SAM 3.1 output is special-token text: parse boxes, ignore mask payloads.
        from onlyyou.sam import parse_boxes

        raw = (
            "<0f>0<|box;x1=179;y1=0;x2=1002;y2=899;w=1200;h=900|>"
            "<|mask;x=0;y=0;data=900,824,~abc|>,1"
            "<|box;x1=10;y1=20;x2=30;y2=40;w=50;h=60|>"
        )
        boxes = parse_boxes(raw)
        self.assertEqual(len(boxes), 2)
        self.assertEqual(boxes[0]["x2"], 1002)
        self.assertEqual(boxes[1]["y2"], 40)

    def test_repairs_prose_answer(self):
        MockState.mode = "prose"
        obs = Observation(mode="labeled", labels=[], owner_command="pay this invoice")
        action = self.client.propose(obs, "D")
        self.assertIsNotNone(action)
        self.assertGreaterEqual(MockState.calls, 2)


if __name__ == "__main__":
    unittest.main()
