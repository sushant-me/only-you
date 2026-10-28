# Omni-Video 2 — feasibility and honest recommendation

Source: <https://github.com/SAIS-FUXI/Omni-Video> (Fudan / Shanghai AI Lab). It is a **video generation and
editing** framework: a text-to-video DiT (OmniVideo2-A14B, or the 1.3B variant) conditioned by Qwen3-VL,
with video-to-video editing.

## Can it run on this machine?

**No.** Checked directly:

| Requirement | This machine | Verdict |
|---|---|---|
| GPU VRAM (A14B) | RTX 4050 Laptop, **6 GB** (recommended 80 GB) | far short |
| PyTorch + CUDA toolchain | **not installed**, no `pip` | missing |
| System RAM | 14 GB total | T5-umt5-xxl + VAE + DiT weights exceed it |
| Disk | 121 GB free | enough, but irrelevant |

The 1.3B DiT is smaller, but the pipeline still needs the T5-XXL text encoder and Qwen3-VL (30B) for the
captioning stage — still far beyond 6 GB. So we **did not fake a run** and the submission does not claim it.

## If you can rent a GPU

An A100/H100 80 GB (or 2×A6000) on a cloud GPU provider for ~1 hour is enough. Then:

```bash
git clone https://github.com/SAIS-FUXI/Omni-Video
# follow its README: python -m venv, pip install -r requirements.txt, download checkpoints
# source clip: use docs/demo-x-vertical.mp4 or a still from docs/img/hero.jpg
cat > /tmp/prompts.jsonl <<'JSONL'
{"sample_id": "you-01", "edit_prompt": "cinematic slow push-in on smart glasses, red rim light, dark room, subtle lens flare", "source_clip_path": "/data/hero.mp4"}
JSONL
GEN_TASK="v2v-A14B" GEN_SIZE="832*480" GEN_FRAME_NUM=41 GEN_SAMPLE_FPS=8 \
  bash tools/inference/inference_omni_e2e.sh
```

## What it should and should not be used for here

- **Good:** 3–6 s atmospheric B-roll (glasses on a table, a red-lit room) for the intro/outro.
- **Bad:** video-to-video editing of the **UI screen recording**. Diffusion models regenerate pixels; the
  UI text, rule IDs and receipt hashes would be garbled, and a demo that shows fake text is worse than no
  B-roll. Never edit the actual demo footage with a generative model.
- It is not a voice tool — it cannot clone or synthesize your voice.

## What actually improves the video

A human voice-over. Record 60–90 s reading `docs/video-3min.md` (or improvise over the captions) and drop
the file here; `make voice VOICE=narration.wav` muxes and loudness-normalises it onto the 2:55 cut:

```bash
make voice VOICE=~/narration.wav     # → docs/demo-3min-voice.mp4
```
