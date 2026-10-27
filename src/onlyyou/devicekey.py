"""Device keys: Ed25519 mandates that a merchant can verify offline.

The demo's HMAC signature proved the mandate was issued by *someone who knows the
secret*. That is enough inside one process and useless to a merchant: a merchant
cannot hold the device secret. This module gives the device a real Ed25519 key
pair (via OpenSSL, no Python crypto dependency) so a mandate can be verified by
anyone holding the public key — which is the whole point of a verifiable
delegation.

Threat model: the private key lives on the device; the merchant only needs
`device.pub.pem`. It proves the principal authorised *this* mandate; it does not
prove the principal is human (enrolment) or that the device is uncompromised.
"""

from __future__ import annotations

import base64
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


class DeviceKeyError(RuntimeError):
    pass


def _openssl(args: list[str]) -> subprocess.CompletedProcess:
    if not shutil.which("openssl"):
        raise DeviceKeyError("openssl not found; install openssl to use Ed25519 mandates")
    proc = subprocess.run(["openssl", *args], capture_output=True)
    if proc.returncode != 0:
        raise DeviceKeyError(proc.stderr.decode(errors="replace")[:300])
    return proc


@dataclass
class DeviceKey:
    directory: Path
    private_path: Path
    public_path: Path
    public_pem: str

    @classmethod
    def create(cls, directory: str | Path) -> "DeviceKey":
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        private = directory / "device.key.pem"
        public = directory / "device.pub.pem"
        if not private.exists():
            _openssl(["genpkey", "-algorithm", "ED25519", "-out", str(private)])
            private.chmod(0o600)
        if not public.exists():
            _openssl(["pkey", "-in", str(private), "-pubout", "-out", str(public)])
        return cls(directory, private, public, public.read_text())

    def sign(self, payload: bytes) -> str:
        with tempfile.TemporaryDirectory() as td:
            msg = Path(td) / "msg.bin"
            sig = Path(td) / "sig.bin"
            msg.write_bytes(payload)
            _openssl(
                [
                    "pkeyutl", "-sign",
                    "-inkey", str(self.private_path),
                    "-rawin", "-in", str(msg),
                    "-out", str(sig),
                ]
            )
            return "ed25519:" + base64.b64encode(sig.read_bytes()).decode()

    @staticmethod
    def verify(payload: bytes, signature: str, public_pem: str) -> bool:
        """Offline verification — what a merchant runs, with no shared secret."""
        if not signature.startswith("ed25519:"):
            return False
        try:
            raw = base64.b64decode(signature.split(":", 1)[1], validate=True)
        except Exception:
            return False
        with tempfile.TemporaryDirectory() as td:
            msg = Path(td) / "msg.bin"
            sig = Path(td) / "sig.bin"
            pub = Path(td) / "pub.pem"
            msg.write_bytes(payload)
            sig.write_bytes(raw)
            pub.write_text(public_pem)
            proc = subprocess.run(
                [
                    "openssl", "pkeyutl", "-verify",
                    "-pubin", "-inkey", str(pub),
                    "-rawin", "-in", str(msg),
                    "-sigfile", str(sig),
                ],
                capture_output=True,
            )
            return proc.returncode == 0
