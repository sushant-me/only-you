"""SAM 3.1 object grounding through the Meta Model API.

SAM returns special-token text over `POST /v1/responses`: one line per frame with
boxes and mask payloads. This module asks for a short noun phrase (e.g. "paper"
or "document"), parses the boxes, and leaves mask decoding to a client library
(`@meta-sam/parser`) or a later iteration.

The boxes are used as scene *grounding* (which region is the document), never as
authority: the label layer still treats everything read from a frame as data.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import urllib.request

RESPONSES_PATH = "/responses"
BOX_RE = re.compile(r"\|box;x1=(\d+);y1=(\d+);x2=(\d+);y2=(\d+);w=(\d+);h=(\d+)\|")
_CACHE: dict[str, dict] = {}

MIME = {b"\x89PNG": "image/png", b"\xff\xd8": "image/jpeg", b"GIF8": "image/gif"}


class SamError(RuntimeError):
    pass


def _mime(image: bytes) -> str:
    for magic, mime in MIME.items():
        if image.startswith(magic):
            return mime
    return "image/png"


def parse_boxes(text: str) -> list[dict[str, int]]:
    """Parse `|box;x1=..;y1=..;x2=..;y2=..;w=..;h=..|` records from SAM output."""
    boxes = []
    for match in BOX_RE.finditer(text or ""):
        x1, y1, x2, y2, w, h = (int(v) for v in match.groups())
        boxes.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2, "w": w, "h": h})
    return boxes


def available() -> bool:
    return bool(os.environ.get("META_API_KEY") and os.environ.get("META_API_BASE"))


def segment(image: bytes, prompt: str = "paper", model: str | None = None) -> dict:
    """Ask SAM 3.1 for a short noun phrase and return its boxes.

    Returns {"model", "prompt", "boxes", "raw_length"} or raises SamError.
    """
    if not available():
        raise SamError("META_API_BASE/META_API_KEY not set")
    cache_key = hashlib.sha256(image + b"\0" + prompt.encode()).hexdigest()
    if cache_key in _CACHE:
        return dict(_CACHE[cache_key], cached=True)
    base = os.environ["META_API_BASE"].rstrip("/")
    key = os.environ["META_API_KEY"]
    name = model or os.environ.get("SAM_MODEL", "sam-3.1")
    body = {
        "model": name,
        "input": [
            {
                "type": "message",
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:{_mime(image)};base64,{base64.b64encode(image).decode()}",
                    },
                ],
            }
        ],
    }
    request = urllib.request.Request(
        base + RESPONSES_PATH,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    timeout = float(os.environ.get("META_API_TIMEOUT", "60"))
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read())
    except Exception as exc:  # noqa: BLE001 - network/provider errors become SamError
        raise SamError(f"SAM request failed: {exc}") from exc
    try:
        text = payload["output"][0]["content"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise SamError("unexpected SAM response") from exc
    result = {"model": name, "prompt": prompt, "boxes": parse_boxes(text), "raw_length": len(text)}
    _CACHE[cache_key] = result
    return dict(result, cached=False)
