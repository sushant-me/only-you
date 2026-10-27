"""DOM provenance: is this text something the user typed, developer chrome,
user-generated content, or content hidden from human eyes?

Prismata (Villa et al., 2026) showed that dynamic trust derivation over the DOM
is the right shape for web agents; this module is a deliberately small version
so the hackathon demo can label a page in milliseconds. It is not a
reimplementation of Prismata — cite it and use it if you need full coverage.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# A short list of the tricks that hide instructions from a human while leaving
# them in the accessibility tree / model context.
_HIDDEN_STYLE_PATTERNS = [
    re.compile(r"display\s*:\s*none", re.I),
    re.compile(r"visibility\s*:\s*hidden", re.I),
    re.compile(r"font-size\s*:\s*0(?:px)?", re.I),
    re.compile(r"opacity\s*:\s*0(?:\.0+)?\s*[;\"']", re.I),
    re.compile(r"color\s*:\s*(?:#fff(?:fff)?|white)\b", re.I),
    re.compile(r"position\s*:\s*absolute\s*;\s*(?:top|left)\s*:\s*-\d{3,}", re.I),
    re.compile(r"text-indent\s*:\s*-\d{3,}", re.I),
]


@dataclass(frozen=True)
class DomOrigin:
    origin: str  # "user_typed" | "hidden" | "page"
    reason: str
    confidence: float = 0.95


def classify_dom_node(attrs: dict[str, Any]) -> DomOrigin:
    """Classify one rendered node.

    Expected attrs (all optional):
      user_typed: bool       the value came from an input the user filled in
      aria_hidden: bool      aria-hidden="true"
      style: str             inline style
      css_class: str         class names (review-card, ad-slot, comment, ...)
      tag: str               element tag
      in_iframe: bool        content from a third-party iframe
    """
    if attrs.get("user_typed"):
        return DomOrigin("user_typed", "value typed by the user")

    if attrs.get("aria_hidden"):
        return DomOrigin("hidden", 'aria-hidden="true"')

    style = str(attrs.get("style", ""))
    for pat in _HIDDEN_STYLE_PATTERNS:
        if pat.search(style):
            return DomOrigin("hidden", f"hidden by style: {style[:60]!r}")

    cls = str(attrs.get("css_class", "")).lower()
    if any(k in cls for k in ("review", "comment", "ad-slot", "sponsored", "ugc", "user-content")):
        return DomOrigin("page", f"user-generated region ({cls[:40]})")

    if attrs.get("in_iframe"):
        return DomOrigin("page", "third-party iframe")

    if str(attrs.get("tag", "")).lower() in {"script", "style", "template"}:
        return DomOrigin("hidden", "non-rendered element")

    return DomOrigin("page", "developer/page content")


def scan_html_snippet(html: str) -> list[DomOrigin]:
    """Best-effort scan of an HTML string; returns one entry per suspicious node.

    This is a demo helper, not a parser. A production version uses the rendered
    accessibility tree plus computed styles from Playwright.
    """
    found: list[DomOrigin] = []
    # Comments are invisible to humans but often visible to agents that read HTML.
    for m in re.finditer(r"<!--(.*?)-->", html, re.S):
        found.append(DomOrigin("hidden", f"HTML comment: {m.group(1)[:40]!r}"))

    for m in re.finditer(r"<([a-zA-Z][a-zA-Z0-9]*)([^>]*)>(.*?)</\1>", html, re.S):
        tag, raw_attrs, inner = m.group(1), m.group(2), m.group(3)
        style = ""
        sm = re.search(r'style\s*=\s*"([^"]*)"', raw_attrs)
        if sm:
            style = sm.group(1)
        aria = 'aria-hidden="true"' in raw_attrs or "aria-hidden='true'" in raw_attrs
        origin = classify_dom_node({"tag": tag, "style": style, "aria_hidden": aria})
        if origin.origin == "hidden":
            found.append(origin)
    return found
