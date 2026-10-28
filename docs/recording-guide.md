# Recording the 3-minute demo

The software is ready. This is the 30-minute recording session.

## Before you hit record (10 min)

```bash
cd only-you-hackathon
cp .env.example .env      # if you have not already; fill META_API_BASE / META_API_KEY / MUSE_MODEL
make web                  # http://127.0.0.1:8000
```

- Open **http://127.0.0.1:8000/?script=full&fakecam=1** in a clean browser window at 1600×900.
- Check the badge next to the title:
  - `model: muse-spark-1.3` (green) — real model, use this for the video.
  - `model: simulated` (amber) — the key did not load; fix `.env` first.
- Test the mic: `arecord -d 3 /tmp/t.wav && aplay /tmp/t.wav`.
- Close notifications and personal tabs.

## Record the screen

Wayland (Hyprland): `wf-recorder -g "$(slurp)" -f demo-raw.mkv`
X11: `ffmpeg -f x11grab -video_size 1600x900 -i :0.0 -f mp4 demo-raw.mp4`
Or OBS at 1600×900 / 30 fps.

## What to capture (one take, hands-free)

Press **▶ run full demo**. The sequence is automatic; talk over it.

| Beat | What appears | Typical wall time |
|---|---|---|
| 1 · grant mandate | mandate card, `valid` | instant |
| 2 · owner pays invoice | DONE · R6-mandate, receipt | 6–7 s |
| 3 · attacker invoice | BLOCKED · R1/R0 | 10–16 s |
| 4 · poster | mask + BLOCKED · R0 | 5–6 s |
| 5 · TV ad | BLOCKED · R0 | 4–5 s |
| 6 · hidden page text | BLOCKED · R0 | 3–5 s |
| 7 · "what did you do today?" | ledger answer, chain intact | instant |

Total ≈ 45–60 s. Then click **run agent task** and let the step trace fill (≈10 s), and optionally **Scan scene** to show Muse Wonder reading the poster (≈3 s).

If a beat takes longer than ~20 s, it is still working (Muse Spark latency); keep talking rather than stopping the take.

## Voice-over without a screen recording

If you send a voice memo instead of recording the screen, mux it onto the captioned cut:

```bash
make voice VOICE=~/narration.wav   # 60–90 s is enough; it is padded/trimmed to 2:55, two-pass -16 LUFS
```

Speak the script from `docs/video-3min.md`; the captions already carry the beats. Record in a quiet room,
phone mic is fine, 44.1/48 kHz mono.

## Cut and export

```bash
ffmpeg -i demo-raw.mkv -vf "scale=1920:1080,fps=30" \
  -c:v libx264 -crf 20 -preset medium -c:a aac -b:a 160k -movflags +faststart demo.mp4
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 demo.mp4
```

Target ≤ 3:00, 1920×1080, under 300 MB. Upload with `docs/youtube-upload.md`.

## If something fails

| Problem | Action |
|---|---|
| Badge says `simulated` | `.env` missing/wrong; the demo still works, but record only after it shows Muse Spark |
| Invoice beat blocked | check the mandate was granted (beat 1) and the app has `electrician` in contacts; re-run the beat |
| Camera unavailable | keep `?fakecam=1`; scene provenance is unchanged |
| Model slow / API error | the gate refuses cleanly; re-run the take. Do not fake the outcome |
| No time to record | use `docs/demo-3min.mp4` (2:55, captioned) and lay your voice-over on it |

## Save the raw file

Keep `demo-raw.mkv` — it is the unedited proof the video was captured from the running product.
