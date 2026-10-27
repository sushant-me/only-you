"""Voice channel: enrolment, verification, and honest failure modes."""

from __future__ import annotations

import io
import math
import struct
import unittest
import wave

from onlyyou.voice import enroll, verify


def wav(f0: float, seconds: float = 1.6, sr: int = 16000, seed: float = 0.0, amp: float = 1.0) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        frames = []
        for i in range(int(seconds * sr)):
            t = i / sr
            v = amp * (
                0.5 * math.sin(2 * math.pi * f0 * t + seed)
                + 0.25 * math.sin(2 * math.pi * 2 * f0 * t)
                + 0.12 * math.sin(2 * math.pi * 3 * f0 * t)
            )
            frames.append(struct.pack("<h", int(max(-1.0, min(1.0, v)) * 30000)))
        wf.writeframes(b"".join(frames))
    return buf.getvalue()


class TestVoice(unittest.TestCase):
    def setUp(self):
        self.voice = enroll([wav(120, seed=0.1), wav(123, seed=0.3), wav(118, seed=0.2)])

    def test_same_voice_accepted(self):
        result = verify(self.voice, wav(121, seed=0.4))
        self.assertTrue(result["accept"], result)
        self.assertLess(result["distance"], result["threshold"])

    def test_different_voice_rejected(self):
        result = verify(self.voice, wav(215, seed=0.5))
        self.assertFalse(result["accept"], result)
        self.assertGreater(result["distance"], result["threshold"])

    def test_silence_rejected(self):
        result = verify(self.voice, wav(0, amp=0.0))
        self.assertFalse(result["accept"])
        self.assertEqual(result["reason"], "not enough speech")

    def test_threshold_is_bounded(self):
        self.assertGreaterEqual(self.voice.threshold, 0.06)
        self.assertLess(self.voice.threshold, 0.5)

    def test_short_clip_rejected(self):
        result = verify(self.voice, wav(120, seconds=0.15))
        self.assertFalse(result["accept"])


if __name__ == "__main__":
    unittest.main()
