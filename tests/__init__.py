"""Test package: keep the suite offline and deterministic.

When a developer has a real `.env` with Meta API credentials, the demo service
would otherwise select the live model and the tests would make network calls.
Tests that want the real model do so explicitly with their own mock endpoint.
"""

import os

os.environ.setdefault("ONLYYOU_MODEL", "simulated")
