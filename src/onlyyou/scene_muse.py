"""Scene reading with Muse Wonder (multimodal), tesseract as the fallback.

Muse Wonder accepts an image in the chat content, so the camera path can use a
Meta multimodal model directly: it returns the text *and* approximate pixel
boxes, which the UI uses for the mask overlay. Tesseract remains the offline
fallback so the demo works without a key and the synthetic OCR benchmark stays
deterministic.
"""

from __future__ import annotations

import base64
import json
import os
import re
from typing import Any

from .model import MetaModelClient

PROMPT = (
    "Read every piece of text in this image. Return ONLY JSON with the keys "
    '"text" (all text, newline-separated) and "lines" (a list of {"bbox":[x,y,w,h] in pixels, '
    '"text": "..."}). No prose, no code fences.'
)


def _extract_json(raw: str) -> dict[str, Any] | None:
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _lines(data: dict[str, Any]) -> list[dict[str, Any]]:
    lines: list[dict[str, Any]] = []
    for item in data.get("lines") or []:
        try:
            bbox = [int(v) for v in item.get("bbox", [])][:4]
            text = str(item.get("text", "")).strip()
        except (TypeError, ValueError):
            continue
        if text and len(bbox) == 4:
            lines.append({"bbox": bbox, "text": text})
    return lines


def muse_read(png: bytes, timeout: int = 90) -> dict[str, Any] | None:
    """Return {"text","lines","reader","model"} from Muse Wonder, or None."""
    if not MetaModelClient.available():
        return None
    model = os.environ.get("MUSE_VISION_MODEL", "muse-wonder-1.0")
    client = MetaModelClient(model=model, timeout=timeout)
    data_url = "data:image/png;base64," + base64.b64encode(png).decode()
    try:
        raw = client.chat(
            [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
            temperature=0.0,
        )
    except Exception:
        return None
    data = _extract_json(raw)
    if data is None:
        return None
    text = str(data.get("text", "")).strip()
    lines = _lines(data)
    if not text and not lines:
        return None
    return {
        "text": text or "\n".join(line["text"] for line in lines),
        "lines": lines,
        "reader": "muse-wonder",
        "model": model,
        "usage": dict(client.stats),
    }
