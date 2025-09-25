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
    # FIX: write a real newline, not the literal "\n"
    with LEDGER.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def last_hash() -> str:
    if not LEDGER.exists() or not LEDGER.read_text().strip():
        return ""
    last = LEDGER.read_text().splitlines()[-1].strip()
    return json.loads(last)["hash"]


def chain() -> list[dict]:
    if not LEDGER.exists():
        return []
    blocks = []
    for line in LEDGER.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            blocks.append(json.loads(line))
        except json.JSONDecodeError:
            # ✅ self-heal: ignore corrupted lines
            continue
    return blocks


def clear_chain() -> None:
    if LEDGER.exists():
        LEDGER.unlink()
