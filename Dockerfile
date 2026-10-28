# ONLY YOU — demo server, one command anywhere.
#   docker build -t only-you . && docker run --rm -p 8000:8000 only-you
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    ONLYYOU_MODEL=simulated

# Optional system tools the demo can use: OCR for scene text, QR for receipts.
RUN apt-get update \
 && apt-get install -y --no-install-recommends tesseract-ocr qrencode ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY src ./src
COPY Makefile README.md LICENSE ./

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/state', timeout=2)" || exit 1

CMD ["python3", "-m", "onlyyou.cli", "web", "--host", "0.0.0.0", "--port", "8000"]
