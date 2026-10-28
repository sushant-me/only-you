"""OpenAPI 3.1 description of the demo HTTP surface.

Hand-written rather than generated: the API is small, and a checked-in spec is
what an integrator or a security reviewer wants to read without running the app.
"""

from __future__ import annotations

from typing import Any

INFO = {
    "title": "ONLY YOU — provenance-gated authority layer (demo)",
    "version": "1.0.0",
    "description": (
        "Every action is a proposal; the gate decides using provenance, the owner's constitution and "
        "signed scoped mandates. Receipts are signed and hash-chained; refusals are receipts too. "
        "The HMAC secret in the demo is public by design; mandate signatures are real Ed25519."
    ),
}

TAGS = [
    {"name": "agent", "description": "Send an input and get a decision, a receipt and the state."},
    {"name": "mandates", "description": "Delegate bounded authority: caps, sub-limits, periods, sub-agents."},
    {"name": "schedules", "description": "Standing instructions that re-check a live mandate at run time."},
    {"name": "policy", "description": "The owner's constitution: edit, dry-run, export/import with review."},
    {"name": "evidence", "description": "Receipts, verification pages, QR codes, audit export and CSV."},
    {"name": "commerce", "description": "Merchant-side mandate verification and checkout."},
    {"name": "voice", "description": "Wearable voice enrollment and command transcription (Muse Wonder)."},
    {"name": "demo", "description": "Reset, frames, guided tasks and the policy dry-run simulator."},
]


def _response(description: str = "OK", example: Any | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"description": description}
    if example is not None:
        body["content"] = {"application/json": {"schema": {"type": "object"}, "example": example}}
    return body


def _op(
    method: str,
    path: str,
    summary: str,
    tag: str,
    body: Any | None = None,
    params: list[dict[str, Any]] | None = None,
) -> tuple[str, str, dict[str, Any]]:
    operation: dict[str, Any] = {
        "summary": summary,
        "tags": [tag],
        "responses": {
            "200": _response(),
            "400": _response("Bad request"),
        },
    }
    if body is not None:
        operation["requestBody"] = {
            "required": True,
            "content": {"application/json": {"schema": {"type": "object"}, "example": body}},
        }
    if params:
        operation["parameters"] = params
    return method, path, operation


OPERATIONS = [
    _op("post", "/api/command", "Send an owner/voice/document input; the gate decides.", "agent",
        {"speaker": "owner", "channel": "document", "text": "pay this invoice",
         "invoice": {"payee": "electrician", "amount": 4500}, "confirms": True}),
    _op("post", "/api/mandate", "Issue a mandate (narrower when parent_id is present).", "mandates",
        {"payees": ["electrician"], "max_amount": 5000, "daily_limit": 1000,
         "payee_limits": {"electrician": 1000}, "period_seconds": 2592000}),
    _op("post", "/api/mandate/revoke", "Revoke one mandate.", "mandates", {"id": "abc123"}),
    _op("post", "/api/mandate/revoke-all", "Panic button: revoke every mandate.", "mandates", {}),
    _op("post", "/api/schedule", "Create a standing instruction under a mandate.", "schedules",
        {"payee": "electrician", "amount": 500, "every_seconds": 2592000, "mandate_id": "abc123"}),
    _op("post", "/api/schedule/run", "Run a standing instruction now (live mandate required).", "schedules",
        {"id": "a1b2c3d4"}),
    _op("post", "/api/policy", "Enable or disable a constitution rule (receipted as R7).", "policy",
        {"rule_id": "R2-payment-over-limit", "enabled": False}),
    _op("post", "/api/policy/diff", "Show what a signed policy bundle would change.", "policy",
        {"bundle": {"format": "only-you-policy/1", "rules": [], "signature": "..."}}),
    _op("post", "/api/policy/import", "Apply a signed policy bundle (receipted as R7).", "policy",
        {"bundle": {"format": "only-you-policy/1", "rules": [], "signature": "..."}}),
    _op("get", "/api/policy/export", "Signed policy snapshot for version control.", "policy"),
    _op("get", "/api/state", "Current mandates, receipts, rules, alerts, schedules and counters.", "agent"),
    _op("post", "/api/simulate", "Dry-run a proposed action without executing it.", "demo",
        {"action": {"kind": "pay", "params": {"payee": "electrician", "amount": 4500}}}),
    _op("post", "/api/merchant-verify", "Offline-style merchant verification of a mandate.", "commerce",
        {"id": "abc123", "action": {"kind": "pay", "params": {"payee": "electrician", "amount": 500}}}),
    _op("post", "/api/checkout", "Verify a presented mandate, then pay through the gate.", "commerce",
        {"id": "abc123", "payee": "electrician", "amount": 4500}),
    _op("post", "/api/voice/enroll", "Enroll the owner's wearable voiceprint.", "voice", {"wav_base64": "..."}),
    _op("post", "/api/voice/verify", "Check a clip against the enrolled voiceprint.", "voice", {"wav_base64": "..."}),
    _op("post", "/api/voice/transcribe", "Transcribe a command clip with Muse Wonder.", "voice",
        {"wav_base64": "..."}),
    _op("get", "/api/receipts", "Filter receipts by decision, rule prefix and free text.", "evidence",
        params=[
            {"name": "decision", "in": "query", "schema": {"type": "string", "enum": ["allow", "ask", "deny"]}},
            {"name": "rule", "in": "query", "schema": {"type": "string"}, "example": "R1"},
            {"name": "q", "in": "query", "schema": {"type": "string"}, "example": "electrician"},
        ]),
    _op("get", "/api/receipts.csv", "CSV export of the filtered receipts.", "evidence",
        params=[{"name": "decision", "in": "query", "schema": {"type": "string"}}]),
    _op("get", "/api/receipt/{id}", "One receipt as JSON with signature and chain status.", "evidence",
        params=[{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}]),
    _op("get", "/api/export", "Self-contained signed audit bundle.", "evidence"),
    _op("get", "/api/qr/{id}.png", "QR code for a receipt's verification URL.", "evidence",
        params=[{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}]),
    _op("post", "/api/reset", "Reset the demo world, ledger, mandates, policy and schedules.", "demo", {}),
]

PATHS: dict[str, dict[str, Any]] = {}
for method, path, operation in OPERATIONS:
    PATHS.setdefault(path, {})[method] = operation

SPEC: dict[str, Any] = {
    "openapi": "3.1.0",
    "info": INFO,
    "servers": [{"url": "http://localhost:8000", "description": "local demo"}],
    "tags": TAGS,
    "paths": PATHS,
}
