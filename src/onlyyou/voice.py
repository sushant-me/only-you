"""On-device voice channel: enrol the owner, verify a command.

Deliberately small and dependency-free (stdlib only): energy gate → 32 ms frames
→ radix-2 FFT → mel filterbank → log → DCT → 13 MFCC → mean+std embedding →
cosine similarity. Enrolment builds a centroid and a threshold from the owner's
own clips.

This is a demonstrator of the *channel architecture*, not an anti-spoofing
speaker model. A cloned voice passes it; a different voice usually does not.
The product claim is the provenance rule (only the enrolled channel is a
command), not the accuracy of this particular embedding. The benchmark reports
the limitation instead of hiding it.
"""

from __future__ import annotations

import io
import math
import struct
import wave
from dataclasses import dataclass, field

TARGET_RATE = 8000
FRAME_SECONDS = 0.032
HOP_SECONDS = 0.016
N_FFT = 512
N_MELS = 24
N_MFCC = 13


# ---------------------------------------------------------------- wav input
def read_wav(data: bytes) -> tuple[list[float], int]:
    """Read a PCM WAV (8/16/32-bit, mono or stereo) into mono floats [-1, 1]."""
    with wave.open(io.BytesIO(data), "rb") as wf:
        channels = wf.getnchannels()
        width = wf.getsampwidth()
        rate = wf.getframerate()
        raw = wf.readframes(wf.getnframes())
    if width == 2:
        samples = [s / 32768.0 for s in struct.unpack("<%dh" % (len(raw) // 2), raw)]
    elif width == 1:
        samples = [(s - 128) / 128.0 for s in raw]
    elif width == 4:
        samples = [s / 2147483648.0 for s in struct.unpack("<%di" % (len(raw) // 4), raw)]
    else:
        raise ValueError(f"unsupported sample width: {width}")
    if channels > 1:
        samples = [sum(samples[i : i + channels]) / channels for i in range(0, len(samples), channels)]
    return samples, rate


def resample(samples: list[float], rate: int, target: int = TARGET_RATE) -> list[float]:
    if rate == target or not samples:
        return samples
    ratio = rate / target
    out = []
    n = int(len(samples) / ratio)
    for i in range(n):
        start = int(i * ratio)
        end = max(start + 1, int((i + 1) * ratio))
        out.append(sum(samples[start:end]) / (end - start))
    return out


# ---------------------------------------------------------------- dsp
def _fft(xs: list[complex]) -> list[complex]:
    n = len(xs)
    a = list(xs)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j |= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    length = 2
    while length <= n:
        ang = -2.0 * math.pi / length
        wlen = complex(math.cos(ang), math.sin(ang))
        for i in range(0, n, length):
            w = 1 + 0j
            half = length // 2
            for k in range(i, i + half):
                u = a[k]
                v = a[k + half] * w
                a[k] = u + v
                a[k + half] = u - v
                w *= wlen
        length <<= 1
    return a


def _mel(hz: float) -> float:
    return 2595.0 * math.log10(1.0 + hz / 700.0)


def _hz(mel: float) -> float:
    return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)


_FILTERS: list[list[tuple[int, float]]] | None = None


def _filters() -> list[list[tuple[int, float]]]:
    global _FILTERS
    if _FILTERS is not None:
        return _FILTERS
    points = [int(N_FFT * _hz(_mel(80) + (_mel(3800) - _mel(80)) * i / (N_MELS + 1)) / TARGET_RATE) for i in range(N_MELS + 2)]
    filters: list[list[tuple[int, float]]] = []
    for m in range(1, N_MELS + 1):
        left, center, right = points[m - 1], points[m], points[m + 1]
        weights = []
        for k in range(left, center):
            if center > left:
                weights.append((k, (k - left) / (center - left)))
        for k in range(center, right):
            if right > center:
                weights.append((k, (right - k) / (right - center)))
        filters.append(weights)
    _FILTERS = filters
    return filters


def _dct(log_energies: list[float]) -> list[float]:
    out = []
    for k in range(N_MFCC):
        total = 0.0
        for n, value in enumerate(log_energies):
            total += value * math.cos(math.pi * k * (n + 0.5) / N_MELS)
        out.append(total)
    return out


def mfcc(samples: list[float]) -> list[list[float]]:
    win = int(FRAME_SECONDS * TARGET_RATE)
    hop = int(HOP_SECONDS * TARGET_RATE)
    if len(samples) < win:
        return []
    frames: list[list[float]] = []
    for start in range(0, len(samples) - win, hop):
        chunk = samples[start : start + win]
        rms = math.sqrt(sum(v * v for v in chunk) / win)
        if rms < 0.004:
            continue
        hann = [chunk[i] * (0.5 - 0.5 * math.cos(2 * math.pi * i / (win - 1))) for i in range(win)]
        spectrum = _fft([complex(v, 0.0) for v in hann] + [0j] * (N_FFT - win))
        power = [abs(spectrum[k]) ** 2 for k in range(N_FFT // 2 + 1)]
        energies = []
        for weights in _filters():
            energies.append(math.log(1e-10 + sum(power[k] * w for k, w in weights)))
        frames.append(_dct(energies))
    return frames


def embed(samples: list[float]) -> list[float]:
    frames = mfcc(samples)
    if not frames:
        return []
    n = len(frames[0])
    mean = [sum(f[i] for f in frames) / len(frames) for i in range(n)]
    std = [
        math.sqrt(sum((f[i] - mean[i]) ** 2 for f in frames) / len(frames)) for i in range(n)
    ]
    vector = mean + std
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))


def distance(a: list[float], b: list[float]) -> float:
    """Euclidean distance between L2-normalised embeddings."""
    if not a or not b or len(a) != len(b):
        return 2.0
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


@dataclass
class Voiceprint:
    centroid: list[float]
    threshold: float
    samples: list[list[float]] = field(default_factory=list)
    self_scores: list[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "enrolled": True,
            "clips": len(self.samples),
            "threshold": round(self.threshold, 4),
            "self_scores": [round(s, 4) for s in self.self_scores],
        }


def enroll(wavs: list[bytes]) -> Voiceprint:
    embeddings = []
    for wav in wavs:
        samples, rate = read_wav(wav)
        vec = embed(resample(samples, rate))
        if vec:
            embeddings.append(vec)
    if len(embeddings) < 1:
        raise ValueError("no usable audio in enrolment clips")
    n = len(embeddings[0])
    centroid = [sum(e[i] for e in embeddings) / len(embeddings) for i in range(n)]
    norm = math.sqrt(sum(v * v for v in centroid)) or 1.0
    centroid = [v / norm for v in centroid]
    self_distances = sorted(distance(e, centroid) for e in embeddings)
    spread = self_distances[-1] if self_distances else 0.0
    threshold = max(0.06, float(spread) * 2.5 + 0.02)
    return Voiceprint(
        centroid=centroid,
        threshold=round(threshold, 4),
        samples=embeddings,
        self_scores=self_distances,
    )


def verify(voiceprint: Voiceprint, wav: bytes) -> dict:
    samples, rate = read_wav(wav)
    resampled = resample(samples, rate)
    n_frames = len(mfcc(resampled))
    vec = embed(resampled)
    if not vec or n_frames < 25:
        return {"distance": 2.0, "threshold": round(voiceprint.threshold, 4), "accept": False,
                "score": 0.0, "frames": n_frames, "reason": "not enough speech"}
    dist = distance(vec, voiceprint.centroid)
    return {
        "distance": round(dist, 4),
        "threshold": round(voiceprint.threshold, 4),
        "accept": dist <= voiceprint.threshold,
        "score": round(max(0.0, 1.0 - dist), 4),
        "frames": n_frames,
    }
