# Credits and third-party notices

ONLY YOU is MIT-licensed (see `LICENSE`). This file records what the project depends on and what was
generated for it — useful for a legal/security review.

## Models and generated assets

- **Muse Spark 1.3** and **Muse Spark 1.3 contributor build** via the **Meta Model API**
  (`api.meta.ai/v1`) produce the agent proposals in the real-model runs.
- **Muse Wonder 1.0** reads camera frames into text and approximate boxes (scene evaluation), and
  transcribes command clips when a key exposes the model.
- **Muse Image 1.0** generated the demo's poster, TV frame, invoice, article and hero image.
  Synthetic scene assets live under `data/` and `src/onlyyou/web/fakecam-*.jpg`.
- **Narration:** the 3-minute cut's voice track is a neural-TTS draft (Edge `en-US-AndrewNeural`) generated
  from `docs/narration-script.md`; it is replaceable with a human recording. No third-party music is used.
- **Share cards / screenshots** were rendered from HTML with headless Chromium or captured from the demo.

## Runtime dependencies

The demo server is **Python standard library only**. Optional system tools:

| Tool | Used for | Licence |
|---|---|---|
| OpenSSL (CLI) | Ed25519 device keys and mandate signatures | Apache-2.0 |
| tesseract | OCR fallback for scene text | Apache-2.0 |
| ImageMagick | demo asset processing / frame generation | ImageMagick licence |
| ffmpeg | demo video assembly and audio muxing | LGPL/GPL (build-dependent) |
| qrencode | receipt QR codes (optional) | LGPL-2.1 |
| Chromium | headless screenshots, browser probes | BSD-style |
| edge-tts (dev only) | synthetic narration draft | GPL-3.0 (tool, not vendored) |

No Python packages are vendored or required. The Docker image installs `tesseract-ocr` and `qrencode`
from Debian packages.

## Data

The demo enrols a single author's voice locally; no audio is retained. The camera scenes are synthetic or
consenting footage. No third-party personal data is included in the repository or the videos.

The human speaker study uses **LibriSpeech dev-clean** (OpenSLR 12), © Vassil Panayotov et al., licensed
**CC BY 4.0** (<https://www.openslr.org/12>). No LibriSpeech audio is committed — only measured distances
and the results JSON — and the dataset's attribution is retained here.

## Attribution

Please credit **ONLY YOU — Sushant Poudel** with a link to <https://github.com/sushant-me/only-you> when
reusing the videos, screenshots or share cards.
