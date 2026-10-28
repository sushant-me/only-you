"""QR codes for receipts: generated server-side, decodable, and linked from pages."""

from __future__ import annotations

import shutil
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from onlyyou.webapp import DemoService, make_handler

HAS_QR = bool(shutil.which("qrencode")) and bool(shutil.which("zbarimg"))


class TestQr(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = DemoService()
        cls.service.grant_mandate({"payees": ["electrician"], "max_amount": 5000})
        cls.mandate_id = cls.service.state()["mandates"][0]["id"]
        result = cls.service.checkout({"id": cls.mandate_id, "payee": "electrician", "amount": 100})
        cls.receipt_id = result["payment"]["receipt"]["id"]
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(cls.service))
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    @unittest.skipUnless(HAS_QR, "qrencode and zbarimg are required")
    def test_qr_decodes_to_verify_url(self):
        with urllib.request.urlopen(self.base + f"/api/qr/{self.receipt_id}.png", timeout=5) as resp:
            self.assertEqual(resp.headers["Content-Type"], "image/png")
            png = resp.read()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
            handle.write(png)
            path = handle.name
        try:
            proc = __import__("subprocess").run(
                ["zbarimg", "--quiet", "--raw", path], capture_output=True, text=True, timeout=10
            )
        finally:
            Path(path).unlink(missing_ok=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        url = proc.stdout.strip()
        self.assertTrue(url.startswith("http://"), url)
        self.assertTrue(url.endswith(f"/verify/{self.receipt_id}"), url)

    def test_verify_page_embeds_qr(self):
        with urllib.request.urlopen(self.base + f"/verify/{self.receipt_id}", timeout=5) as resp:
            page = resp.read().decode()
        self.assertIn(f"/api/qr/{self.receipt_id}.png", page)
        self.assertIn("Scan to open this receipt", page)

    def test_unknown_receipt_qr_is_404(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(self.base + "/api/qr/nope.png", timeout=5)
        self.assertEqual(ctx.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
