#!/usr/bin/env python3
"""Verify an ONLY YOU audit export offline.

    python3 tools/verify_audit.py only-you-audit.json

Checks the receipt chain (HMAC + prev_hash) and every mandate signature (Ed25519
over the canonical payload) using only the bundle. This is the "don't trust us,
check the file" path a compliance reviewer needs.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from onlyyou.devicekey import DeviceKey  # noqa: E402
from onlyyou.mandates import Mandate  # noqa: E402
from onlyyou.receipts import DEMO_SECRET  # noqa: E402

MANDATE_FIELDS = ("id", "principal", "scope", "payees", "max_amount", "issued_at", "expires_at", "nonce", "note")


def verify_bundle(bundle: dict[str, Any], secret: bytes = DEMO_SECRET) -> dict[str, Any]:
    receipts = bundle.get("receipts", [])
    errors: list[dict[str, str]] = []
    prev = "0" * 64
    for receipt in receipts:
        payload = {k: v for k, v in receipt.items() if k != "signature"}
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        expected = hmac.new(secret, canonical, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, str(receipt.get("signature", ""))):
            errors.append({"receipt": str(receipt.get("id")), "error": "signature"})
        if receipt.get("prev_hash") != prev:
            errors.append({"receipt": str(receipt.get("id")), "error": "chain"})
        prev = str(receipt.get("signature", ""))

    pem = str(bundle.get("device_public_key", ""))
    mandates = []
    for raw in bundle.get("mandates", []):
        signature = str(raw.get("signature", ""))
        ok = False
        if signature.startswith("ed25519:") and pem:
            mandate = Mandate(**{field: raw.get(field) for field in MANDATE_FIELDS})
            ok = DeviceKey.verify(mandate.canonical().encode(), signature, pem)
        mandates.append({"id": raw.get("id"), "signature_ok": ok})

    return {
        "receipts_ok": not errors,
        "receipt_errors": errors,
        "mandates_ok": all(m["signature_ok"] for m in mandates),
        "mandates": mandates,
        "chain_head": prev,
        "bundle_chain_ok": bool(bundle.get("chain", {}).get("ok")),
        "receipt_count": len(receipts),
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: verify_audit.py only-you-audit.json", file=sys.stderr)
        return 2
    bundle = json.loads(Path(argv[1]).read_text())
    result = verify_bundle(bundle)
    print(json.dumps(result, indent=2))
    ok = result["receipts_ok"] and result["mandates_ok"] and result["bundle_chain_ok"]
    print("VERIFIED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
