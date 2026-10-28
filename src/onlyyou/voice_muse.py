"""Spoken commands with Muse Voice Transcribe (primary) and Muse Wonder (fallback).

Muse Voice Transcribe is Meta's speech-to-text model: `POST /v1/asr/transcribe`
with a multipart `request` part and a 16/24 kHz mono PCM WAV. The transcript is
*text*: it still has to pass the voice check and the gate, exactly like typed input.
"""

from __future__ import annotations

import base64
import json
import os
import urllib.request
import uuid

from .model import MetaModelClient

PROMPT = "Transcribe the speech in this audio exactly. Return only the transcript, no commentary."
ASR_MODEL = "muse-voice-transcribe-1.0"


def _asr_transcribe(wav: bytes, timeout: int) -> dict[str, str] | None:
    base = os.environ.get("META_API_BASE", "").rstrip("/")
    key = os.environ.get("META_API_KEY", "")
    if not base or not key:
        return None
    boundary = f"----onlyyou{uuid.uuid4().hex}"
    request_part = json.dumps(
        {
            "mode": "PUSH_TO_TALK",
            "model": os.environ.get("MUSE_ASR_MODEL", ASR_MODEL),
            "audioEncoding": "WAV",
        }
    ).encode()
    body = b"".join(
        [
            f"--{boundary}\r\n".encode(),
            b'Content-Disposition: form-data; name="request"\r\n',
            b"Content-Type: application/json\r\n\r\n",
            request_part,
            b"\r\n",
            f"--{boundary}\r\n".encode(),
            b'Content-Disposition: form-data; name="audio"; filename="audio.wav"\r\n',
            b"Content-Type: audio/wav\r\n\r\n",
            wav,
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )
    request = urllib.request.Request(
        f"{base}/asr/transcribe?sessionId=onlyyou-{uuid.uuid4().hex[:12]}",
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read())
    except Exception:
        return None
    text = str(payload.get("transcript", "")).strip()
    if not text:
        return None
    return {"text": text, "model": os.environ.get("MUSE_ASR_MODEL", ASR_MODEL)}


def transcribe_wav(wav: bytes, timeout: int = 60) -> dict[str, str] | None:
    """Return {"text","model"} from Muse Voice Transcribe, then Muse Wonder."""
    asr = _asr_transcribe(wav, timeout)
    if asr is not None:
        return asr
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
