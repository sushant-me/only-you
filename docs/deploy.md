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
cp .env.example .env      # fill in your key locally (gitignored)
docker run --rm -p 8000:8000 --env-file .env -e ONLYYOU_MODEL=meta only-you-demo
```

`docker-compose.yml` reads the three Meta variables from your environment (or compose's `.env`) and
defaults `ONLYYOU_MODEL` to `simulated`; the key is never baked into the image.

The image includes the optional system tools the demo uses (`tesseract-ocr` for scene text, `qrencode`
for receipt QR codes). Healthcheck: `GET /api/state` every 30 s. Port: 8000.

## Compose

```bash
docker compose --env-file .env up --build
```

`ONLYYOU_MODEL=simulated` (the default) keeps the demo deterministic and offline; `meta` calls the
Meta Model API. See `docs/limitations.md` for what is demo-only (the HMAC receipt secret) and what is
real (Ed25519 mandate signatures).

## Local

```bash
make web     # http://127.0.0.1:8000
make judge   # tests + live-server smoke + self-audit
```
