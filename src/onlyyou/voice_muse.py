"""Spoken commands with Muse Wonder (audio-in), tesseract-style fallback is not possible.

Muse Wonder accepts an `input_audio` part, so the demo can transcribe a real spoken
command with a Meta model instead of typing it. The transcript is *text*: it still
has to pass the voice check and the gate, exactly like typed input.
"""

from __future__ import annotations

import base64
import os

from .model import MetaModelClient

PROMPT = "Transcribe the speech in this audio exactly. Return only the transcript, no commentary."


def transcribe_wav(wav: bytes, timeout: int = 60) -> dict[str, str] | None:
    """Return {"text","model"} from Muse Wonder, or None when unavailable."""
    if not MetaModelClient.available():
        return None
    model = os.environ.get("MUSE_AUDIO_MODEL", "muse-wonder-1.0")
    client = MetaModelClient(model=model, timeout=timeout)
    audio = base64.b64encode(wav).decode()
    try:
        raw = client.chat(
            [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {"type": "input_audio", "input_audio": {"data": audio, "format": "wav"}},
                    ],
                }
            ],
            temperature=0.0,
        )
    except Exception:
        return None
    text = raw.strip().strip('"')
    if not text:
        return None
    return {"text": text, "model": model}
