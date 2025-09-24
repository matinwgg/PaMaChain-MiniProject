"""
A minimal append-only blockchain ledger with ECDSA signatures.
"""
import json, time, hashlib
from pathlib import Path
from ecdsa import SigningKey, NIST256p

LEDGER = Path.home() / ".pamachain_ledger.jsonl"
KEY = SigningKey.generate(curve=NIST256p)

def _hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def append_block(entry: dict) -> dict:
    entry = dict(entry)
    entry["timestamp"] = time.time()
    entry["prev_hash"] = last_hash()
    raw = json.dumps(entry, sort_keys=True)
    entry["hash"] = _hash(raw)
    entry["sig"] = KEY.sign(raw.encode()).hex()
    LEDGER.open("a").write(json.dumps(entry) + "\\n")
    return entry

def last_hash() -> str:
    if not LEDGER.exists():
        return ""
    *_, last = LEDGER.read_text().splitlines()
    return json.loads(last)["hash"]

def chain() -> list[dict]:
    if not LEDGER.exists():
        return []
    return [json.loads(line) for line in LEDGER.read_text().splitlines()]

def clear_chain() -> None:
    if LEDGER.exists():
        LEDGER.unlink()