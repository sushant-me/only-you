"""The static browser playground ships with the repo and points at real assets."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestPlayground(unittest.TestCase):
    def test_playground_is_present_and_self_contained(self):
        page = (ROOT / "docs" / "playground.html").read_text()
        self.assertIn("ONLY YOU", page)
        self.assertIn("R0-source-not-authoritative", page)
        self.assertIn("verify chain", page)
        self.assertIn("img/invoice-scene.jpg", page)
        self.assertTrue((ROOT / "docs" / "img" / "invoice-scene.jpg").is_file())
        # no backend dependency: no fetch/XHR calls on this page
        self.assertNotIn("fetch(", page)
        self.assertNotIn("XMLHttpRequest", page)


if __name__ == "__main__":
    unittest.main()
