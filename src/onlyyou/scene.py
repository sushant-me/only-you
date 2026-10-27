"""Scene provenance: text that exists in the physical world is *data*.

The 2026 result to design against is "Devil in the Lens" (arXiv:2607.10269):
physically embedded text hijacks wearable VLMs at up to 96% ASR in simulation
and 60% in real environments. The defense in this kit is architectural, not a
detector: any text observed through the camera is labelled SCENE and can never
be promoted to an instruction.

Running SAM 3.1 at 30 fps on a laptop is not realistic. The demo runs it
offline on a handful of hero frames, caches the masks as JSON assets, and at
demo time overlays the cached masks. The visual is identical and the demo is
stable. See `data/hero_frames/README.md`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .provenance import Channel, Input


@dataclass(frozen=True)
class TextSurface:
    """One text-bearing region found in a frame."""

    frame_id: str
    bbox: tuple[int, int, int, int]  # x, y, w, h
    text: str
    surface_kind: str = "sign"  # sign | screen | poster | shirt | label | whiteboard
    mask_score: float = 0.0

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TextSurface":
        bbox = tuple(d.get("bbox", (0, 0, 0, 0)))
        return cls(
            frame_id=str(d.get("frame_id", "")),
            bbox=(int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])),
            text=str(d.get("text", "")),
            surface_kind=str(d.get("surface_kind", "sign")),
            mask_score=float(d.get("mask_score", 0.0)),
        )


class CachedMaskProvider:
    """Loads SAM 3.1 masks + OCR text from JSON sidecars.

    Expected sidecar format (one file per frame, or one file with a list):

        {"frame_id": "poster-01",
         "surfaces": [{"bbox": [10, 20, 300, 120],
                       "text": "IGNORE PREVIOUS INSTRUCTIONS ...",
                       "surface_kind": "poster",
                       "mask_score": 0.94}]}
    """

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else None
        self._frames: dict[str, list[TextSurface]] = {}
        if self.path and self.path.exists():
            self._load(self.path)

    def _load(self, path: Path) -> None:
        raw = json.loads(path.read_text(encoding="utf-8"))
        records = raw if isinstance(raw, list) else [raw]
        for record in records:
            fid = str(record.get("frame_id", ""))
            self._frames[fid] = [TextSurface.from_dict(s) for s in record.get("surfaces", [])]

    def surfaces(self, frame_id: str) -> list[TextSurface]:
        return list(self._frames.get(frame_id, []))

    def frames(self) -> list[str]:
        return sorted(self._frames)


def scene_inputs(surfaces: Iterable[TextSurface], source_prefix: str = "scene") -> list[Input]:
    """Convert detected text surfaces into routed inputs (always SCENE / data)."""
    inputs: list[Input] = []
    for i, s in enumerate(surfaces):
        inputs.append(
            Input(
                channel=Channel.SCENE,
                text=s.text,
                source_id=f"{source_prefix}:{s.frame_id}:{i}",
                signals={
                    "frame_id": s.frame_id,
                    "bbox": list(s.bbox),
                    "surface_kind": s.surface_kind,
                    "mask_score": s.mask_score,
                },
            )
        )
    return inputs


def overlay_svg(surfaces: Iterable[TextSurface], width: int, height: int) -> str:
    """Return an SVG overlay highlighting the text surfaces (the demo money shot)."""
    rects = []
    for s in surfaces:
        x, y, w, h = s.bbox
        rects.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" '
            f'stroke="#ff2d55" stroke-width="3" rx="6"/>'
            f'<text x="{x}" y="{max(y - 6, 12)}" fill="#ff2d55" font-size="14">'
            f"{_svg_escape(s.surface_kind)}: {_svg_escape(s.text[:32])}</text>"
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">' + "".join(rects) + "</svg>"
    )


def _svg_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )
