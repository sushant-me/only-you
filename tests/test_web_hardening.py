"""The demo server still bounds what a visitor can send it."""

from __future__ import annotations

import json
import socket
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from onlyyou.webapp import MAX_BODY, DemoService, make_handler


class TestWebHardening(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name) / "web"
        root.mkdir()
        (root / "index.html").write_text("<h1>ok</h1>")
        (root / ".secret").write_text("nope")
        (root / "pyproject.toml").write_text("[project]")
        cls.service = DemoService()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(cls.service, root=root))
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.tmp.cleanup()

    def raw(self, request: bytes) -> bytes:
        with socket.create_connection((self.server.server_address[0], self.server.server_address[1]), timeout=5) as s:
            s.sendall(request)
            chunks = []
            while True:
                data = s.recv(4096)
                if not data:
                    break
                chunks.append(data)
                if len(b"".join(chunks)) > 65536:
                    break
            return b"".join(chunks)

    def test_oversized_body_rejected(self):
        resp = self.raw(
            b"POST /api/command HTTP/1.1\r\nHost: x\r\nContent-Type: application/json\r\n"
            + f"Content-Length: {MAX_BODY + 1}\r\n\r\n".encode()
        )
        self.assertIn(b"413", resp.split(b"\r\n", 1)[0])

    def test_bad_content_length_rejected(self):
        resp = self.raw(b"POST /api/command HTTP/1.1\r\nHost: x\r\nContent-Length: abc\r\n\r\n")
        self.assertIn(b"400", resp.split(b"\r\n", 1)[0])

    def test_dotfile_forbidden(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(self.base + "/.secret", timeout=5)
        self.assertEqual(ctx.exception.code, 403)

    def test_path_traversal_forbidden(self):
        resp = self.raw(b"GET /../pyproject.toml HTTP/1.1\r\nHost: x\r\n\r\n")
        self.assertIn(b"403", resp.split(b"\r\n", 1)[0])

    def test_unsafe_suffix_forbidden(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(self.base + "/pyproject.toml", timeout=5)
        self.assertEqual(ctx.exception.code, 403)

    def test_security_header_present(self):
        with urllib.request.urlopen(self.base + "/api/state", timeout=5) as resp:
            self.assertEqual(resp.headers.get("X-Content-Type-Options"), "nosniff")
            self.assertEqual(resp.headers.get("X-Frame-Options"), "DENY")
            self.assertEqual(resp.headers.get("Referrer-Policy"), "no-referrer")
            self.assertIn("camera=(self)", resp.headers.get("Permissions-Policy", ""))
            self.assertEqual(resp.headers.get("Cross-Origin-Opener-Policy"), "same-origin")
            json.load(resp)


if __name__ == "__main__":
    unittest.main()


class TestApiValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(DemoService()))
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def post(self, path, payload):
        req = urllib.request.Request(
            self.base + path, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status, json.load(resp)
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read() or b"{}")

    def test_non_numeric_amount_is_400_not_dropped(self):
        code, body = self.post("/api/mandate", {"payees": "electrician", "max_amount": "lots"})
        self.assertEqual(code, 400)
        self.assertIn("error", body)

    def test_negative_amount_rejected(self):
        code, body = self.post("/api/mandate", {"payees": ["electrician"], "max_amount": -5})
        self.assertEqual(code, 400)

    def test_empty_payees_rejected(self):
        code, _ = self.post("/api/mandate", {"payees": [], "max_amount": 100})
        self.assertEqual(code, 400)

    def test_malformed_command_still_answers(self):
        code, body = self.post("/api/command", {"speaker": None, "channel": None, "text": None})
        self.assertEqual(code, 200)
        self.assertIn("outcome", body)


class TestTranscribeValidation(unittest.TestCase):
    def test_bad_audio_payload_is_400_or_error(self):
        from onlyyou.webapp import DemoService

        result = DemoService().transcribe({"clip": "not-base64!!!"})
        self.assertIn("error", result)
