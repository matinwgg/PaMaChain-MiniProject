"""Minimal local keystore metadata storage.

Only the password salt and an authenticated password-check value are stored.
Secrets must never be written to this file. For a production wallet, use an OS
keychain/HSM-backed secret store instead.
"""

from __future__ import annotations

import json
import os
import tempfile
from contextlib import suppress
from pathlib import Path

from .paths import keystore_path


def _chmod_fd(fd: int, mode: int) -> None:
    """Set owner-only permissions where the platform supports it."""
    if hasattr(os, "fchmod"):
        os.fchmod(fd, mode)


def _write_atomic(path: Path, payload: str) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=".pamachain-", dir=path.parent)
    try:
        _chmod_fd(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def save_keystore(salt: bytes, verifier: str | None = None) -> None:
    """Persist the salt and optional password verifier atomically."""
    if len(salt) != 16:
        raise ValueError("salt must be exactly 16 bytes")
    if verifier is not None and not isinstance(verifier, str):
        raise ValueError("verifier must be a string or None")

    document: dict[str, str] = {"salt": salt.hex()}
    if verifier:
        document["verifier"] = verifier
    _write_atomic(
        keystore_path(),
        json.dumps(document, separators=(",", ":"), sort_keys=True),
    )


# Backwards-compatible alias for callers that only have a salt.
def save_salt(salt: bytes) -> None:
    save_keystore(salt, None)


def load_keystore() -> dict[str, object] | None:
    """Load the keystore document, or return None when no vault exists."""
    path = keystore_path()
    if not path.exists():
        return None
    with suppress(OSError):
        os.chmod(path, 0o600)
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        salt = bytes.fromhex(document["salt"])
        verifier = document.get("verifier")
        if verifier is not None and not isinstance(verifier, str):
            raise ValueError("verifier must be a string")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid PaMaChain keystore") from exc
    if len(salt) != 16:
        raise ValueError("invalid PaMaChain keystore salt")
    return {"salt": salt, "verifier": verifier}


def load_salt() -> bytes | None:
    """Load and validate the persisted salt."""
    document = load_keystore()
    return document["salt"] if document else None  # type: ignore[return-value]


def keystore_exists() -> bool:
    return keystore_path().is_file()
