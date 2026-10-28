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
            json.load(resp)


if __name__ == "__main__":
    unittest.main()
