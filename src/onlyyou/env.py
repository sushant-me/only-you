"""Load a local `.env` without a dependency.

The hackathon keys live in `.env` (gitignored). Benchmarks and the demo should
pick them up without the builder having to remember `export $(grep …)`. Values
already present in the process environment win; nothing is printed.
"""

from __future__ import annotations

import os
from pathlib import Path

KEYS = ("META_API_BASE", "META_API_KEY", "MUSE_MODEL", "OPEN_WEIGHTS_BASE", "OPEN_WEIGHTS_KEY", "OPEN_WEIGHTS_MODEL", "ONLYYOU_WEBHOOK_URL")


def load_env(path: str | Path | None = None) -> dict[str, str]:
    """Read KEY=VALUE lines from `.env` (current dir by default). Returns what it set."""
    env_path = Path(path or ".env")
    if not env_path.exists():
        return {}
    loaded: dict[str, str] = {}
    for raw in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key in KEYS and value and not os.environ.get(key):
            os.environ[key] = value
            loaded[key] = value
    return loaded
