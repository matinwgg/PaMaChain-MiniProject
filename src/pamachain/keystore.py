"""Minimal local keystore metadata storage.

Only the password salt is stored. Secrets must never be written to this file.
For a production wallet, use an OS keychain/HSM-backed secret store instead.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

KEYSTORE = Path.home() / ".pamachain_keystore.json"


def save_salt(salt: bytes) -> None:
    """Persist a validated salt atomically with owner-only permissions."""
    if len(salt) != 16:
        raise ValueError("salt must be exactly 16 bytes")

    KEYSTORE.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    payload = json.dumps({"salt": salt.hex()}, separators=(",", ":"))
    fd, tmp_name = tempfile.mkstemp(prefix=".pamachain-", dir=KEYSTORE.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, KEYSTORE)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def load_salt() -> bytes | None:
    """Load and validate the persisted salt."""
    if not KEYSTORE.exists():
        return None
    try:
        document = json.loads(KEYSTORE.read_text(encoding="utf-8"))
        salt = bytes.fromhex(document["salt"])
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid PaMaChain keystore") from exc
    if len(salt) != 16:
        raise ValueError("invalid PaMaChain keystore salt")
    return salt


def keystore_exists() -> bool:
    return KEYSTORE.is_file()
