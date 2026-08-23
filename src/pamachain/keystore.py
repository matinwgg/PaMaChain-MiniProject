"""Local PaMaChain key metadata storage with restrictive file permissions."""
import json
import os
from pathlib import Path

KEYSTORE = Path.home() / ".pamachain_keystore.json"


def _write(data: dict) -> None:
    KEYSTORE.parent.mkdir(parents=True, exist_ok=True)
    temporary = KEYSTORE.with_suffix(".tmp")
    temporary.write_text(json.dumps(data), encoding="utf-8")
    os.chmod(temporary, 0o600)
    temporary.replace(KEYSTORE)
    os.chmod(KEYSTORE, 0o600)


def save_salt(salt: bytes) -> None:
    if len(salt) != 16:
        raise ValueError("Salt must be exactly 16 bytes")
    _write({"version": 1, "salt": salt.hex()})


def load_salt() -> bytes | None:
    if not KEYSTORE.exists():
        return None
    try:
        data = json.loads(KEYSTORE.read_text(encoding="utf-8"))
        salt = bytes.fromhex(data["salt"])
        return salt if len(salt) == 16 else None
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return None


def keystore_exists() -> bool:
    return KEYSTORE.exists()
