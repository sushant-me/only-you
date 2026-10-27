"""Agentic multi-step task: browse → extract → decide → act → report.

This is the "agentic use-case" surface: one goal, several tool steps, a decision
under a mandate, an action, and a receipt the wearer can inspect. It reuses the
same gate as the single-command demo, so the security story does not change when
the agent does more.

The page is fetched for real (http(s) or file://); hidden regions are extracted
separately and labelled as hidden DOM content. The invoice is a document input,
so its fields can supply arguments to an owner instruction — never the
instruction itself.
"""

from __future__ import annotations

import re
import urllib.request
from typing import Any

from .agent import Agent, Arm
from .provenance import Channel, Input
from .scenarios import Scenario

_HIDDEN_ATTR = re.compile(
    r'<([a-zA-Z0-9]+)[^>]*(?:style\s*=\s*"[^"]*'
    r'(?:display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*0|opacity\s*:\s*0|'
    r'color\s*:\s*(?:#fff|#ffffff|white))[^"]*"|aria-hidden\s*=\s*"true")[^>]*>(.*?)</\1>',
    re.S | re.I,
)
_HIDDEN_CLASS = re.compile(
    r'<([a-zA-Z0-9]+)[^>]*class\s*=\s*"[^"]*'
    r'(?:hidden|sr-only|visually-hidden|d-none|invisible)[^"]*"[^>]*>(.*?)</\1>',
    re.S | re.I,
)
_SCRIPT = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.S | re.I)
_TAG = re.compile(r"<[^>]+>")


def fetch_html(url: str, timeout: int = 15) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_page(html: str) -> tuple[str, list[str]]:
    """Return (visible text, hidden snippets). Hidden text stays in the context."""
    hidden = []
    visible_html = html
    for pattern in (_HIDDEN_ATTR, _HIDDEN_CLASS):
        for match in pattern.finditer(visible_html):
            text = _TAG.sub(" ", match.group(2))
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                hidden.append(text)
        visible_html = pattern.sub(" ", visible_html)
    visible_html = _SCRIPT.sub(" ", visible_html)
    visible = _TAG.sub(" ", visible_html)
    visible = re.sub(r"\s+", " ", visible).strip()
    return visible, hidden


def _describe(action: Any) -> str:
    return action.describe() if action is not None else "nothing"


def run_task(
    agent: Agent,
    goal: str,
    page_url: str,
    invoice: dict[str, Any],
    owner_confirms: bool = True,
    pay_limit: int | None = None,
    max_steps: int = 8,
) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []

    def step(sid: str, title: str, status: str, detail: str = "") -> None:
        steps.append({"id": sid, "title": title, "status": status, "detail": detail})

    step("browse", "Browse the page", "running", page_url)
    try:
        html = fetch_html(page_url)
    except Exception as exc:  # network/file errors are a normal task outcome
        step("browse", "Browse the page", "error", str(exc)[:200])
        return {"goal": goal, "steps": steps, "outcome": "error", "answer": "could not read the page"}
    step("browse", "Browse the page", "ok", f"{len(html)} bytes")

    visible, hidden = extract_page(html)
    step(
        "extract",
        "Extract visible text and hidden regions",
        "ok",
        f"{len(visible)} visible chars, {len(hidden)} hidden region(s)",
    )

    inputs = [
        Input(Channel.VOICE, goal, "voice:owner", {"speaker_score": 0.97, "proximity": True}),
        Input(Channel.WEB, visible, "dom:page", {"user_typed": False}),
    ]
    for i, text in enumerate(hidden):
        inputs.append(Input(Channel.WEB, text, f"dom:hidden-{i}", {"hidden": True}))
    inputs.append(
        Input(
            Channel.DOCUMENT,
            str(invoice.get("text", "INVOICE")),
            "doc:invoice",
            {"invoice": invoice, "trusted_document": True},
        )
    )

    scenario = Scenario(
        id="task",
        kind="benign",
        channel="web",
        goal="pay",
        owner_command=goal,
        inputs=inputs,
        expected_outcome="executed",
        owner_confirms=owner_confirms,
        pay_limit=int(pay_limit if pay_limit is not None else invoice.get("limit", 1000)),
        note="multi-step task",
    )

    result = agent.run(scenario, Arm.D_FULL)
    step("decide", "Decide under the mandate", "ok" if result.action else "blocked", _describe(result.action))
    step(
        "gate",
        "Apply constitution, mandate and provenance",
        "ok" if result.verdict.decision.value == "allow" else result.verdict.decision.value,
        f"{result.verdict.rule}: {result.verdict.reason}",
    )
    step("act", "Execute or refuse", result.outcome, result.tool_result.detail if result.tool_result else "")
    if result.receipt is not None:
        step(
            "receipt",
            "File a signed receipt",
            "ok" if result.receipt_ok else "error",
            f"{result.receipt.id} verified={result.receipt_ok}",
        )

    receipts = agent.ledger.receipts if agent.ledger is not None else []
    blocked = sum(1 for r in receipts if r.verdict.get("decision") == "deny")
    allowed = sum(1 for r in receipts if r.verdict.get("decision") == "allow")
    ignored = len(hidden) if result.outcome == "executed" else 0
    answer = (
        f"I completed the task: {_describe(result.action)} — {result.outcome}. "
        + (f"I ignored {ignored} hidden instruction region(s) because page text is data. " if ignored else "")
        + f"{allowed} action(s) and {blocked} refusal(s) are in the ledger"
        + (", chain verified." if agent.ledger is not None and agent.ledger.verify_chain() else ".")
    )
    step("report", "Explain what happened", "ok", answer)
    return {
        "goal": goal,
        "steps": steps,
        "outcome": result.outcome,
        "action": result.action.to_dict() if result.action else None,
        "verdict": result.verdict.to_dict(),
        "receipt_id": result.receipt.id if result.receipt else None,
        "answer": answer,
    }
