"""Tamper-evident local ledger with persistent ECDSA signatures."""
import hashlib
import json
import os
import time
from pathlib import Path

from ecdsa import NIST256p, SigningKey, VerifyingKey

LEDGER = Path.home() / ".pamachain_ledger.jsonl"
SIGNING_KEY_FILE = Path.home() / ".pamachain_ledger_signing_key"


def _signing_key() -> SigningKey:
    if SIGNING_KEY_FILE.exists():
        return SigningKey.from_string(SIGNING_KEY_FILE.read_bytes(), curve=NIST256p)
    key = SigningKey.generate(curve=NIST256p)
    SIGNING_KEY_FILE.write_bytes(key.to_string())
    os.chmod(SIGNING_KEY_FILE, 0o600)
    return key


def _hash(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _canonical(block: dict) -> str:
    return json.dumps(block, sort_keys=True, separators=(",", ":"))


def append_block(entry: dict) -> dict:
    if not isinstance(entry, dict):
        raise TypeError("Ledger entry must be a dictionary")
    block = dict(entry)
    block["timestamp"] = time.time()
    block["prev_hash"] = last_hash()
    raw = _canonical(block)
    block["hash"] = _hash(raw)
    block["sig"] = _signing_key().sign(raw.encode("utf-8")).hex()
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(block, sort_keys=True) + "\n")
    return block


def last_hash() -> str:
    blocks = chain()
    return blocks[-1]["hash"] if blocks else ""


def chain() -> list[dict]:
    if not LEDGER.exists():
        return []
    blocks = []
    with LEDGER.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                blocks.append(json.loads(line))
    return blocks


def verify_chain() -> bool:
    blocks = chain()
    if not blocks:
        return True
    public_key = _signing_key().verifying_key
    previous_hash = ""
    for block in blocks:
        try:
            signature = bytes.fromhex(block["sig"])
            stored_hash = block["hash"]
            unsigned = {k: v for k, v in block.items() if k not in {"hash", "sig"}}
            raw = _canonical(unsigned)
            if block.get("prev_hash", "") != previous_hash or _hash(raw) != stored_hash:
                return False
            public_key.verify(signature, raw.encode("utf-8"))
            previous_hash = stored_hash
        except (KeyError, ValueError, TypeError):
            return False
    return True


def clear_chain() -> None:
    if LEDGER.exists():
        LEDGER.unlink()
