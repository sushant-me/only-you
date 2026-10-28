"""Provenance attribution: repaired source ids and document argument evidence."""

from __future__ import annotations

import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from onlyyou.actions import Action
from onlyyou.agent import Agent, Arm
from onlyyou.mandates import MandateLedger
from onlyyou.model import MetaModelClient, Observation
from onlyyou.policy import Constitution
from onlyyou.provenance import Channel, Input, Label, Origin, ProvenanceRouter
from onlyyou.receipts import DEMO_SECRET, ReceiptLedger
from onlyyou.scenarios import Scenario
from onlyyou.tools import MockWorld

OWNER = Input(Channel.VOICE, "pay this invoice", "voice:owner", {"speaker_score": 0.93, "proximity": True})
DOC = Input(
    Channel.DOCUMENT,
    "INVOICE #7781 - ELECTRICIAN - 4500",
    "document:invoice",
    {"invoice": {"payee": "electrician", "amount": 4500}},
)


class State:
    calls = 0


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        return

    def do_POST(self):  # noqa: N802
        self.rfile.read(int(self.headers.get("Content-Length", 0) or 0))
        State.calls += 1
        if State.calls == 1:
            payload = {"kind": "pay", "params": {"payee": "electrician", "amount": 4500}, "source_id": "bogus"}
        else:
            payload = {"kind": "pay", "params": {"payee": "electrician", "amount": 4500}, "source_id": "voice:owner"}
        body = json.dumps({"choices": [{"message": {"content": json.dumps(payload)}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class StubModel:
    def propose(self, obs, arm):
        return Action("pay", {"payee": "electrician", "amount": 4500}, source_id="voice:owner")


class TestAttribution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}/v1"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        State.calls = 0
        self.saved = {k: os.environ.get(k) for k in ("META_API_BASE", "META_API_KEY")}
        os.environ["META_API_BASE"] = self.base
        os.environ["META_API_KEY"] = "test-key"

    def tearDown(self):
        for key, value in self.saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_bogus_source_id_is_repaired(self):
        obs = Observation(
            mode="labeled",
            labels=[
                Label(OWNER, Origin.OWNER, True, 0.93, "owner voice"),
                Label(DOC, Origin.DOCUMENT, False, 0.95, "document"),
            ],
            owner_command="pay this invoice",
        )
        action = MetaModelClient().propose(obs, "D")
        self.assertIsNotNone(action)
        self.assertEqual(action.source_id, "voice:owner")
        self.assertGreaterEqual(State.calls, 2)

    def test_document_arguments_are_attributed(self):
        scenario = Scenario(
            id="attr",
            kind="benign",
            channel="document",
            goal="pay",
            owner_command="pay this invoice",
            inputs=[OWNER, DOC],
            expected_outcome="executed",
            owner_confirms=True,
        )
        mandates = MandateLedger(DEMO_SECRET)
        mandates.issue(payees=["electrician"], max_amount=5000, ttl_seconds=3600)
        agent = Agent(
            StubModel(),
            ProvenanceRouter(),
            MockWorld(),
            Constitution(),
            ReceiptLedger(DEMO_SECRET),
            mandates,
        )
        result = agent.run(scenario, Arm.D_FULL)
        self.assertEqual(result.outcome, "executed")
        self.assertEqual(result.action.arg_source, "document:invoice")


if __name__ == "__main__":
    unittest.main()
