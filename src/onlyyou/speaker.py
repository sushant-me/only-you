"""Speaker identity as an *authorization* channel.

Voice assistants recognise you to personalise. ONLY YOU recognises you to
decide whether the utterance is a command at all. A stranger saying
"Hey Meta, send $500" is not a command with a low confidence score; it is not
a command.

`SpeakerVerifier` is a thin interface so the demo can run without audio
dependencies. Plug in a real embedding model (ECAPA-TDNN via SpeechBrain,
WeSpeaker, or Resemblyzer) by implementing `embed()` and `score()`.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


@dataclass
class Enrollment:
    name: str
    embedding: list[float]
    threshold: float = 0.72


class SpeakerVerifier:
    """Enroll one owner, then score candidate utterances.

    `embed()` is the pluggable part. The default implementation is a
    deterministic hash-based pseudo-embedding used by the offline demo and
    tests; it is NOT a real speaker model. Replace it for real audio:

        from resemblyzer import VoiceEncoder
        encoder = VoiceEncoder()
        verifier.embed_fn = lambda wav_bytes: encoder.embed_utterance(wav_bytes)
    """

    def __init__(self, embedding_dim: int = 32, threshold: float = 0.72) -> None:
        self.embedding_dim = embedding_dim
        self.threshold = threshold
        self.enrollment: Enrollment | None = None
        self.embed_fn = self._hash_embed

    # -- pluggable embedding ----------------------------------------------
    def _hash_embed(self, audio: bytes) -> list[float]:
        digest = hashlib.sha512(audio).digest()
        vals = [b / 255.0 - 0.5 for b in digest[: self.embedding_dim]]
        return vals

    def embed(self, audio: bytes) -> list[float]:
        return list(self.embed_fn(audio))

    # -- enrollment --------------------------------------------------------
    def enroll(self, samples: Iterable[bytes], name: str = "owner") -> Enrollment:
        embs = [self.embed(s) for s in samples]
        if not embs:
            raise ValueError("need at least one enrollment sample")
        dim = len(embs[0])
        centroid = [sum(e[i] for e in embs) / len(embs) for i in range(dim)]
        self.enrollment = Enrollment(name=name, embedding=centroid, threshold=self.threshold)
        return self.enrollment

    def score(self, audio: bytes) -> float:
        if self.enrollment is None:
            return 0.0
        return round(_cosine(self.embed(audio), self.enrollment.embedding), 4)

    def is_owner(self, audio: bytes) -> bool:
        return self.score(audio) >= self.threshold

    # -- persistence -------------------------------------------------------
    def save(self, path: str | Path) -> None:
        if self.enrollment is None:
            raise ValueError("nothing enrolled")
        Path(path).write_text(json.dumps(asdict(self.enrollment), indent=2), encoding="utf-8")

    def load(self, path: str | Path) -> Enrollment:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.enrollment = Enrollment(**data)
        return self.enrollment


class ConstantVerifier:
    """Test double: returns a fixed score regardless of input."""

    def __init__(self, score: float) -> None:
        self._score = score

    def score(self, audio: bytes) -> float:  # noqa: ARG002
        return self._score

    def is_owner(self, audio: bytes) -> bool:
        return self._score >= 0.72
