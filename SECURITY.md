# Security policy

ONLY YOU is a hackathon demo of an **authority layer** for wearable agents: provenance labels, a
constitution, Ed25519-signed mandates, and hash-chained receipts. Security review is welcome — the
honest scope is in [`docs/threat-model.md`](docs/threat-model.md) and
[`docs/limitations.md`](docs/limitations.md).

## Reporting a vulnerability

Please open a **private security advisory**:
<https://github.com/sushant-me/only-you/security/advisories/new>

Do not open a public issue for a bypass. This is a solo, unfunded project: I aim to acknowledge reports
within **7 days** and will credit you in the advisory unless you prefer otherwise. There is no bug bounty.

Useful reports include: a way to make an action execute without a command-capable source; a mandate
that authorises outside its scope/payee/cap/period; a receipt that verifies after tampering; a way to
read another user's state (the demo has one user by design — say so if that surprises you); a crash or
resource exhaustion from bounded input; or a header/CSP issue in the demo server.

## What is demo-only (not a vulnerability)

These are stated in the docs and are deliberate:

- **Receipt HMAC secret is public** (`DEMO_SECRET` in `src/onlyyou/receipts.py`). The chain is
  tamper-*evident* for the demo, not a production key. Production roots this in the device secure element.
- **No TEE / secure element / attestation** is implemented. Mandate signatures are real Ed25519, but the
  private key lives on disk in the demo.
- **Mock world**: payments, locks and files are in-memory; nothing touches a real payment rail or device.
- **Voice check is not anti-spoofing**; a cloned voice is out of scope for this prototype.
- **SAM 3.1 masks and Muse voice transcription are not integrated** (documented as roadmap, not claims).
- The alert webhook is best-effort; a SIEM integration in production needs durable queueing and mTLS.

## Defensive details already in the repo

- Mandates: Ed25519 over a canonical payload, verified offline by merchants.
- Receipts: HMAC-SHA256 hash chain; `tools/verify_audit.py` re-checks an exported bundle offline.
- Server: 8 MB body cap, path traversal/dotfile guards, `nosniff`, `X-Frame-Options: DENY`,
  `Referrer-Policy: no-referrer`, `Permissions-Policy`, COOP/CORP; typed 400/500 handling.
- Self-audit (`tools/audit.py`) fails the build on committed secrets, broken tests or stale artifacts.
