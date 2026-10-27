"""Instruction vs. data, decided before the model sees a token.

The core claim of ONLY YOU: prompt injection is not a classification problem,
it is a routing problem. An input that arrives on a non-authoritative channel
is data — it can be read, quoted, summarised and reasoned over, but it can
never become an instruction. That decision is deterministic and cheap; the
language model is only consulted for ambiguity *after* routing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable

DEFAULT_SPEAKER_THRESHOLD = 0.72

ORIGIN_LABELS = {
    "owner": "your voice",
    "stranger": "a voice that isn't yours",
    "page": "page content",
    "hidden": "hidden page content",
    "scene": "scene text",
    "document": "a document",
    "qr": "a QR payload",
    "unknown": "an unknown source",
}


def origin_label(origin: "Origin | str") -> str:
    value = origin.value if isinstance(origin, Origin) else str(origin)
    return ORIGIN_LABELS.get(value, value)


class Channel(str, Enum):
    VOICE = "voice"
    AMBIENT_AUDIO = "ambient_audio"
    WEB = "web"
    SCENE = "scene"
    DOCUMENT = "document"
    QR = "qr"


class Origin(str, Enum):
    OWNER = "owner"
    STRANGER = "stranger"
    PAGE = "page"
    HIDDEN = "hidden"
    SCENE = "scene"
    DOCUMENT = "document"
    QR = "qr"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Input:
    """One piece of content reaching the agent, with the signals needed to label it."""

    channel: Channel
    text: str = ""
    source_id: str = ""
    signals: dict[str, Any] = field(default_factory=dict)
    # How well this payload evades a prompt-only defense (0 = obvious, 1 = stealthy).
    # Used only by the offline simulator; real runs use the model itself.
    stealth: float = 0.0

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Input":
        return cls(
            channel=Channel(d["channel"]),
            text=d.get("text", ""),
            source_id=d.get("source_id", ""),
            signals=dict(d.get("signals", {})),
            stealth=float(d.get("stealth", 0.0)),
        )


@dataclass(frozen=True)
class Label:
    input: Input
    origin: Origin
    command_capable: bool
    confidence: float
    reason: str

    @property
    def text(self) -> str:
        return self.input.text

    @property
    def source_id(self) -> str:
        return self.input.source_id

    @property
    def is_data(self) -> bool:
        return not self.command_capable

    @property
    def origin_label(self) -> str:
        return origin_label(self.origin)


class ProvenanceRouter:
    """Labels each input as OWNER / STRANGER / PAGE / HIDDEN / SCENE / DOCUMENT / QR.

    Rules (v0.1):
      voice           -> OWNER iff speaker score >= threshold AND proximity
      ambient audio   -> STRANGER (TV, radio, stranger)
      web             -> OWNER iff the text was typed by the user; hidden = HIDDEN; else PAGE
      scene           -> SCENE (text seen through the camera is never a command)
      document        -> DOCUMENT (read as data; the owner must confirm actions)
      qr              -> QR (a decoded payload is data)
    """

    def __init__(
        self,
        speaker_threshold: float = DEFAULT_SPEAKER_THRESHOLD,
        require_proximity: bool = True,
        require_signed_signals: bool = False,
        sensor_bus: object | None = None,
    ) -> None:
        self.speaker_threshold = speaker_threshold
        self.require_proximity = require_proximity
        self.require_signed_signals = require_signed_signals
        self.sensor_bus = sensor_bus

    def label(self, inp: Input) -> Label:
        ch = inp.channel

        if self.require_signed_signals:
            ok = bool(self.sensor_bus and getattr(self.sensor_bus, "verify", lambda _i: False)(inp))
            if not ok:
                return Label(
                    inp, Origin.UNKNOWN, False, 0.0,
                    "unsigned sensor data (no valid sensor envelope)",
                )

        if ch is Channel.VOICE:
            score = float(inp.signals.get("speaker_score", 0.0))
            proximity = bool(inp.signals.get("proximity", False))
            owner = score >= self.speaker_threshold and (
                proximity or not self.require_proximity
            )
            return Label(
                inp,
                Origin.OWNER if owner else Origin.STRANGER,
                owner,
                score,
                "voice matches enrolled owner" if owner else "voice not the enrolled owner",
            )

        if ch is Channel.AMBIENT_AUDIO:
            return Label(inp, Origin.STRANGER, False, 0.99, "ambient audio is not a command channel")

        if ch is Channel.WEB:
            dom_origin = str(inp.signals.get("dom_origin", "page"))
            # Web content is NEVER a command channel. A page can ship a script that
            # pre-fills a textarea, and the DOM cannot prove a human typed it.
            # Owner commands come from the microphone (speaker-verified) only.
            if dom_origin == "hidden":
                return Label(inp, Origin.HIDDEN, False, 0.98, "hidden page content")
            if dom_origin == "user_typed":
                return Label(
                    inp, Origin.PAGE, False, 0.9,
                    "web text is never a command channel (owner commands come from the mic)",
                )
            return Label(inp, Origin.PAGE, False, 0.95, "page content")

        if ch is Channel.SCENE:
            return Label(inp, Origin.SCENE, False, 0.99, "text in the physical scene")

        if ch is Channel.DOCUMENT:
            return Label(inp, Origin.DOCUMENT, False, 0.95, "document content")

        if ch is Channel.QR:
            return Label(inp, Origin.QR, False, 0.99, "decoded QR payload")

        return Label(inp, Origin.UNKNOWN, False, 0.0, "unrecognised channel")

    def route(self, inputs: Iterable[Input]) -> list[Label]:
        return [self.label(i) for i in inputs]

    # -- convenience -------------------------------------------------------
    @staticmethod
    def commands(labels: Iterable[Label]) -> list[Label]:
        return [l for l in labels if l.command_capable]

    @staticmethod
    def data(labels: Iterable[Label]) -> list[Label]:
        return [l for l in labels if not l.command_capable]


def render_labeled(labels: Iterable[Label]) -> str:
    """Human-readable view of a routed observation (used by the demo and logs)."""
    out: list[str] = []
    for label in labels:
        tag = "COMMAND" if label.command_capable else f"DATA:{label.origin.value}"
        out.append(f"[{tag} | {label.source_id}] {label.text}")
    return "\n".join(out)
