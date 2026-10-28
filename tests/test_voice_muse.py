"""Muse Wonder audio-in transcription: parsing, empty answers, missing key."""

from __future__ import annotations

import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from onlyyou.voice_muse import transcribe_wav

WAV = b"RIFF" + b"\x00" * 40 + b"WAVE"


class State:
    text = "pay this invoice"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        return

    def do_POST(self):  # noqa: N802
        self.rfile.read(int(self.headers.get("Content-Length", 0) or 0))
        body = json.dumps({"choices": [{"message": {"content": State.text}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class TestVoiceMuse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}/v1"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        self.saved = {k: os.environ.get(k) for k in ("META_API_BASE", "META_API_KEY", "MUSE_AUDIO_MODEL")}
        os.environ["META_API_BASE"] = self.base
        os.environ["META_API_KEY"] = "test-key"
        os.environ["MUSE_AUDIO_MODEL"] = "muse-wonder-mock"

    def tearDown(self):
        for key, value in self.saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_transcribes_text(self):
        State.text = "pay this invoice"
        result = transcribe_wav(WAV)
        self.assertIsNotNone(result)
        self.assertEqual(result["text"], "pay this invoice")
        self.assertEqual(result["model"], "muse-wonder-mock")

    def test_empty_answer_returns_none(self):
        State.text = ""
        try:
            self.assertIsNone(transcribe_wav(WAV))
        finally:
            State.text = "pay this invoice"

    def test_missing_key_returns_none(self):
        os.environ.pop("META_API_KEY", None)
        self.assertIsNone(transcribe_wav(WAV))


if __name__ == "__main__":
    unittest.main()
