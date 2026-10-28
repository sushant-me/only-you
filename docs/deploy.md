# Deploy — ONLY YOU demo

The demo is a single Python process (stdlib only) with an in-memory world. No database, no queue, no
external service is required to run it.

## Docker (no Python on the host)

```bash
docker build -t only-you-demo .
docker run --rm -p 8000:8000 only-you-demo
# open http://127.0.0.1:8000/?script=full&fakecam=1
```

`docker compose up --build` works the same way. Pass Meta credentials to use the real models instead of
the simulated one:

```bash
docker run --rm -p 8000:8000 \
  -e ONLYYOU_MODEL=meta \
  -e META_API_KEY=... -e META_API_BASE=https://api.meta.ai/v1 -e MUSE_MODEL=muse-spark-1.3 \
  only-you-demo
```

The image includes the optional system tools the demo uses (`tesseract-ocr` for scene text, `qrencode`
for receipt QR codes). Healthcheck: `GET /api/state` every 30 s. Port: 8000.

## Compose

```bash
META_API_KEY=... MUSE_MODEL=muse-spark-1.3 docker compose up --build
```

`ONLYYOU_MODEL=simulated` (the default) keeps the demo deterministic and offline; `meta` calls the
Meta Model API. See `docs/limitations.md` for what is demo-only (the HMAC receipt secret) and what is
real (Ed25519 mandate signatures).

## Local

```bash
make web     # http://127.0.0.1:8000
make judge   # tests + live-server smoke + self-audit
```
