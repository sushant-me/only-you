"""Scene OCR through the tesseract CLI.

No Python imaging dependency: the browser (or a test fixture) sends a PNG, we
write it to a temp file, run `tesseract ... tsv`, and return text lines with
pixel boxes. Those boxes become the mask overlay and the evidence in the receipt.

The provenance rule is independent of OCR quality: whatever text is found in the
scene is labelled SCENE and is data. OCR confidence changes the *evidence*, not
the authority.
"""

from __future__ import annotations

import shutil
import statistics
import subprocess
import tempfile
from pathlib import Path


class OcrError(RuntimeError):
    pass


def ocr_png(png: bytes, psm: int = 3) -> dict:
    if not shutil.which("tesseract"):
        raise OcrError("tesseract not found; install tesseract to scan frames")
    with tempfile.TemporaryDirectory() as td:
        image = Path(td) / "frame.png"
        image.write_bytes(png)
        proc = subprocess.run(
            ["tesseract", str(image), "stdout", "--psm", str(psm), "tsv"],
            capture_output=True,
        )
    if proc.returncode != 0:
        raise OcrError(proc.stderr.decode(errors="replace")[:300])

    lines: list[dict] = []
    current: dict | None = None
    for row in proc.stdout.decode(errors="replace").splitlines()[1:]:
        cols = row.split("\t")
        if len(cols) < 12:
            continue
        level, _page, block, par, line = cols[0], cols[1], cols[2], cols[3], cols[4]
        if level != "5":
            continue
        text = cols[11].strip()
        if not text:
            continue
        try:
            conf = float(cols[10])
            left, top, width, height = (int(cols[i]) for i in (6, 7, 8, 9))
        except ValueError:
            continue
        key = (block, par, line)
        if current is None or current["_key"] != key:
            current = {
                "_key": key,
                "text": "",
                "box": [left, top, width, height],
                "confidence": conf,
            }
            lines.append(current)
        current["text"] = (current["text"] + " " + text).strip()
        x0, y0, x1, y1 = current["box"]
        current["box"] = [min(x0, left), min(y0, top), max(x1 + width, left + width), max(y1 + height, top + height)]

    for line in lines:
        line.pop("_key", None)
        x0, y0, x1, y1 = line["box"]
        line["bbox"] = [x0, y0, x1 - x0, y1 - y0]
        line.pop("box", None)
    confidence = round(statistics.fmean(l["confidence"] for l in lines), 2) if lines else 0.0
    return {
        "text": "\n".join(l["text"] for l in lines).strip(),
        "lines": lines,
        "confidence": confidence,
    }
