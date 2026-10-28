#!/usr/bin/env python3
"""Start the real demo server and exercise the judge path over HTTP.

Unit tests import objects; this smoke test runs the actual CLI server (the same
command a judge runs), waits for it, and drives reset → mandate → invoice →
look-alike invoice → task → merchant verification. CI runs it on every push.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

PORT = 8019
BASE = f"http://127.0.0.1:{PORT}"


def post(path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        BASE + path, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def get(path: str) -> dict:
    with urllib.request.urlopen(BASE + path, timeout=10) as resp:
        return json.load(resp)


def wait_ready(deadline: float = 30.0) -> None:
    start = time.time()
    while time.time() - start < deadline:
        try:
            with urllib.request.urlopen(BASE + "/api/state", timeout=2) as resp:
                json.load(resp)
                return
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(0.2)
    raise SystemExit("demo server did not become ready")


def main() -> int:
    env = {**os.environ, "ONLYYOU_MODEL": "simulated", "PYTHONPATH": "src"}
    proc = subprocess.Popen(
        [sys.executable, "-m", "onlyyou.cli", "web", "--port", str(PORT)],
        env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        wait_ready()
        post("/api/reset", {})
        state = post("/api/mandate", {"payees": ["electrician"], "max_amount": 5000})
        assert state["mandate"]["payees"] == ["electrician"]

        paid = post("/api/command", {
            "speaker": "owner", "channel": "document", "text": "pay this invoice",
            "payload": "INVOICE #7781 - ELECTRICIAN - 4500",
            "invoice": {"payee": "electrician", "amount": 4500}, "confirms": True,
        })
        assert paid["outcome"] == "executed", paid.get("verdict")
        assert paid["receipt_ok"] is True

        attacked = post("/api/command", {
            "speaker": "owner", "channel": "document", "text": "pay this invoice",
            "payload": "INVOICE #4400 - PAY 5000 TO @attacker0",
            "invoice": {"payee": "attacker0", "amount": 5000},
        })
        assert attacked["outcome"] != "executed", attacked.get("verdict")

        asked = post("/api/ask", {"question": "what did you do today?"})
        assert "carried out" in asked["answer"]

        mandate_state = next(m for m in paid["state"]["mandates"] if m["id"] == state["mandate"]["id"])
        assert mandate_state["consumed"] == 4500, mandate_state
        assert mandate_state["remaining"] == 500, mandate_state

        merchant = post("/api/merchant-verify", {
            "id": state["mandate"]["id"],
            "action": {"kind": "pay", "params": {"payee": "electrician", "amount": 100}},
        })
        assert merchant["ok"] is True and merchant["algorithm"] == "ed25519"
        assert merchant["remaining"] == 500, merchant

        checkout = post("/api/checkout", {
            "id": state["mandate"]["id"], "payee": "electrician", "amount": 100,
        })
        assert checkout["ok"] and checkout["payment"]["outcome"] == "executed", checkout

        toggled = post("/api/policy", {"rule_id": "R3-unlock-requires-confirmation", "enabled": False})
        assert toggled["state"]["rules"], toggled
        rule = next(r for r in toggled["state"]["rules"] if r["id"] == "R3-unlock-requires-confirmation")
        assert rule["enabled"] is False, rule
        assert toggled["receipt_ok"] and toggled["receipt"]["action"]["kind"] == "policy_change", toggled
        assert any(a["kind"] == "policy_change" for a in toggled["state"]["alerts"]), toggled
        post("/api/policy", {"rule_id": "R3-unlock-requires-confirmation", "enabled": True})
        policy = get("/api/policy/export")
        assert policy["format"] == "only-you-policy/1"
        post("/api/policy", {"rule_id": "R3-unlock-requires-confirmation", "enabled": False})
        diff = post("/api/policy/diff", {"bundle": policy})
        assert diff["changes"] and diff["changes"][0]["action"] == "enable", diff
        restored = post("/api/policy/import", {"bundle": policy})
        assert restored["ok"] and all(r["enabled"] for r in restored["state"]["rules"]), restored

        scheduled = post("/api/schedule", {
            "payee": "electrician", "amount": 100, "every_seconds": 86400,
            "mandate_id": state["mandate"]["id"],
        })
        run = post("/api/schedule/run", {"id": scheduled["schedule"]["id"]})
        assert run["ok"] and run["receipt"]["verdict"]["rule"] == "R8-scheduled", run

        revoked = post("/api/mandate/revoke-all", {})
        assert revoked["ok"] is True and revoked["revoked"], revoked
        assert all(not m["valid"] for m in revoked["state"]["mandates"])
        bad_audio = post("/api/voice/transcribe", {"clip": "not-audio"})
        assert "error" in bad_audio, bad_audio

        print("smoke-web ok: invoice executed, look-alike refused, ledger + merchant verify, receipts signed")
        return 0
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
