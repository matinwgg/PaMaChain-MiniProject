"""
Simple file-based keystore for master key metadata.
"""
import json
from pathlib import Path

KEYSTORE = Path.home() / ".pamachain_keystore.json"

def save_salt(salt: bytes) -> None:
    KEYSTORE.write_text(json.dumps({"salt": salt.hex()}))

def load_salt() -> bytes | None:
    if not KEYSTORE.exists():
        return None
    return bytes.fromhex(json.loads(KEYSTORE.read_text())["salt"])

def keystore_exists() -> bool:
    return KEYSTORE.exists()
# --- IGNORE ---