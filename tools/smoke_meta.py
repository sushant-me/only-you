#!/usr/bin/env python3
"""One real call to the Meta Model API — verifies base URL, key and model.

Usage:
    python3 tools/smoke_meta.py              # dry run: check env only
    python3 tools/smoke_meta.py --call       # one real chat completion
    python3 tools/smoke_meta.py --list-models

Reads META_API_BASE / META_API_KEY / MUSE_MODEL from the environment (or .env
via `export $(grep -v '^#' .env | xargs)`). Never prints the key.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request


def _env(name: str) -> str:
    return os.environ.get(name, "").strip()


def _request(method: str, url: str, key: str, body: dict | None = None) -> tuple[int, str, float]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
    )
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read().decode(), time.time() - started
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode(errors="replace"), time.time() - started


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--call", action="store_true", help="send one chat completion")
    ap.add_argument("--list-models", action="store_true", help="GET /models")
    args = ap.parse_args()

    base = _env("META_API_BASE").rstrip("/")
    key = _env("META_API_KEY")
    model = _env("MUSE_MODEL") or "muse-spark-1.3"

    missing = [n for n, v in (("META_API_BASE", base), ("META_API_KEY", key)) if not v]
    if missing:
        print(f"missing env: {', '.join(missing)}")
        print("cp .env.example .env, fill it, then: export $(grep -v '^#' .env | xargs)")
        return 2
    print(f"base={base} model={model} key=set({len(key)} chars)")

    if args.list_models:
        status, body, dt = _request("GET", f"{base}/models", key)
        print(f"GET /models -> {status} in {dt * 1000:.0f} ms")
        if status == 200:
            try:
                data = json.loads(body)
                ids = [m.get("id") for m in data.get("data", [])]
                print("models:", ", ".join(str(i) for i in ids[:40]))
            except Exception:
                print(body[:1000])
        else:
            print(body[:1000])
        return 0 if status == 200 else 1

    if not args.call:
        print("dry run ok — add --call for one real completion")
        return 0

    body = {
        "model": model,
        "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
        "temperature": 0,
    }
    status, resp, dt = _request("POST", f"{base}/chat/completions", key, body)
    print(f"POST /chat/completions -> {status} in {dt * 1000:.0f} ms")
    if status != 200:
        print(resp[:1500])
        if status == 404:
            print("hint: check META_API_BASE path (try .../v1) and that the model id exists")
        return 1
    try:
        content = json.loads(resp)["choices"][0]["message"]["content"]
        print("reply:", content[:200])
    except Exception:
        print(resp[:1000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
