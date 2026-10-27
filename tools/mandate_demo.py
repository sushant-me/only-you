#!/usr/bin/env python3
"""Issue an Ed25519 mandate, then verify it the way a merchant would — offline.

    python3 tools/mandate_demo.py --out /tmp/mandate
    # writes mandate.json + device.pub.pem, prints VERIFIED / REJECTED

The merchant check uses only OpenSSL and the public key. No shared secret, no
call to the agent, no platform trust.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from onlyyou.devicekey import DeviceKey  # noqa: E402
from onlyyou.mandates import MandateLedger, merchant_verify  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/mandate-demo")
    ap.add_argument("--payee", default="electrician")
    ap.add_argument("--max", type=int, default=5000)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    key = DeviceKey.create(out)
    ledger = MandateLedger(b"demo-ledger-secret", device_key=key)
    mandate = ledger.issue(payees=[args.payee], max_amount=args.max, ttl_seconds=24 * 3600)
    (out / "mandate.json").write_text(json.dumps(mandate.to_dict(), indent=2))
    print(f"mandate {mandate.id}: pay ≤ {args.max} to {args.payee} until {mandate.expires_at:.0f}")
    print(f"public key: {out / 'device.pub.pem'}")

    action = {"kind": "pay", "params": {"payee": args.payee, "amount": args.max - 500}}
    ok, why = merchant_verify(mandate.to_dict(), action, key.public_pem)
    print(f"merchant verify: {'VERIFIED' if ok else 'REJECTED'} — {why}")
    tampered = mandate.to_dict()
    tampered["max_amount"] = 999999
    bad, bad_why = merchant_verify(tampered, action, key.public_pem)
    print(f"tampered mandate: {'VERIFIED' if bad else 'REJECTED'} — {bad_why}")
    return 0 if ok and not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
