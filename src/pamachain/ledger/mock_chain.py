"""Append-only ledger primitives with persistent signing identity and verification."""

import hashlib
import json
import os
import time
from pathlib import Path

from ecdsa import NIST256p, SigningKey, VerifyingKey

LEDGER = Path.home() / ".pamachain_ledger.jsonl"
SIGNING_KEY_FILE = Path.home() / ".pamachain_ledger_signing_key.pem"


def _load_or_create_key() -> SigningKey:
    if SIGNING_KEY_FILE.exists():
        return SigningKey.from_pem(SIGNING_KEY_FILE.read_bytes())
    key = SigningKey.generate(curve=NIST256p)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(SIGNING_KEY_FILE, flags, 0o600)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(key.to_pem())
    except Exception:
        try:
            SIGNING_KEY_FILE.unlink()
        except FileNotFoundError:
            pass
        raise
    return key


KEY = _load_or_create_key()
VERIFYING_KEY = KEY.get_verifying_key()


def _canonical(entry: dict) -> str:
    return json.dumps(entry, sort_keys=True, separators=(",", ":"))


def _hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def append_block(entry: dict) -> dict:
    block = dict(entry)
    block["timestamp"] = time.time()
    block["prev_hash"] = last_hash()
    raw = _canonical(block)
    block["hash"] = _hash(raw)
    block["sig"] = KEY.sign(raw.encode()).hex()
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(block, sort_keys=True) + "\n")
    return block


def last_hash() -> str:
    blocks = chain(verify=False)
    return blocks[-1]["hash"] if blocks else ""


def chain(*, verify: bool = True) -> list[dict]:
    if not LEDGER.exists():
        return []
    blocks: list[dict] = []
    with LEDGER.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                blocks.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Corrupted ledger record at line {line_number}") from exc
    if verify:
        verify_chain(blocks)
    return blocks


def verify_chain(blocks: list[dict] | None = None) -> bool:
    blocks = blocks if blocks is not None else chain(verify=False)
    previous_hash = ""
    for index, block in enumerate(blocks):
        stored_hash = block.get("hash")
        signature = block.get("sig")
        if not stored_hash or not signature:
            raise ValueError(f"Ledger block {index} is missing integrity metadata")
        payload = dict(block)
        del payload["hash"]
        del payload["sig"]
        raw = _canonical(payload)
        if _hash(raw) != stored_hash:
            raise ValueError(f"Ledger block {index} hash verification failed")
        if block.get("prev_hash", "") != previous_hash:
            raise ValueError(f"Ledger block {index} previous-hash verification failed")
        try:
            VERIFYING_KEY.verify(bytes.fromhex(signature), raw.encode())
        except Exception as exc:
            raise ValueError(f"Ledger block {index} signature verification failed") from exc
        previous_hash = stored_hash
    return True


def clear_chain() -> None:
    if LEDGER.exists():
        LEDGER.unlink()
