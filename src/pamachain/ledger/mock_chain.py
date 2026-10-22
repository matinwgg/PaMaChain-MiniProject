"""Append-only ledger primitives with a persistent signing identity.

The ledger is a local JSONL hash chain. Each block is signed with an ECDSA
P-256 key and the latest head is written to a separate anchor file so that
tail truncation and accidental deletion are detected. This is tamper-evident,
not tamper-proof: an attacker who can rewrite both the ledger and its signing
key can rewrite history. A production system must anchor the head in an
independent trust store (or a real chain).
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from contextlib import contextmanager, suppress
from pathlib import Path
from typing import Iterator

from ecdsa import NIST256p, SigningKey, VerifyingKey

from ..paths import anchor_path, ledger_path, lock_path, signing_key_path

try:  # POSIX advisory locking; Windows falls back to no inter-process lock.
    import fcntl
except ImportError:  # pragma: no cover - Windows
    fcntl = None


@contextmanager
def _locked(path: Path, *, exclusive: bool) -> Iterator[None]:
    """Serialise ledger writers (and readers) with an advisory file lock."""
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with lock_path(path).open("a+b") as handle:
        if fcntl is not None:
            fcntl.flock(
                handle.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
            )
        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _load_or_create_key(path: Path | None = None) -> SigningKey:
    key_file = path or signing_key_path()
    if key_file.exists():
        with suppress(OSError):
            os.chmod(key_file, 0o600)
        return SigningKey.from_pem(key_file.read_bytes())

    key_file.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    key = SigningKey.generate(curve=NIST256p)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        fd = os.open(key_file, flags, 0o600)
    except FileExistsError:
        # Another first-run process won the race; use the persisted key.
        return SigningKey.from_pem(key_file.read_bytes())
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(key.to_pem())
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        with suppress(FileNotFoundError):
            key_file.unlink()
        raise
    return key


def _verifying_key(path: Path | None = None) -> VerifyingKey:
    key_file = path or signing_key_path()
    if not key_file.exists():
        raise ValueError("ledger signing key is missing")
    return SigningKey.from_pem(key_file.read_bytes()).get_verifying_key()


def _key_fingerprint(verifying_key: VerifyingKey) -> str:
    return hashlib.sha256(verifying_key.to_der()).hexdigest()


def _canonical(entry: dict) -> str:
    return json.dumps(entry, sort_keys=True, separators=(",", ":"))


def _hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def _read_last_line(path: Path) -> str:
    """Read the final non-empty line without loading the whole ledger."""
    if not path.exists() or path.stat().st_size == 0:
        return ""
    with path.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        position = handle.tell()
        buffer = b""
        while position > 0:
            read_size = min(4096, position)
            position -= read_size
            handle.seek(position)
            buffer = handle.read(read_size) + buffer
            candidate = buffer.rstrip(b"\n")
            if b"\n" in candidate:
                return candidate.rsplit(b"\n", 1)[-1].decode("utf-8")
        return buffer.strip().decode("utf-8")


def last_hash() -> str:
    line = _read_last_line(ledger_path())
    if not line:
        return ""
    try:
        block = json.loads(line)
    except json.JSONDecodeError as exc:
        raise ValueError("Corrupted ledger tail") from exc
    value = block.get("hash")
    if not isinstance(value, str) or not value:
        raise ValueError("Corrupted ledger tail")
    return value


def _write_anchor(head_hash: str, fingerprint: str) -> None:
    path = anchor_path()
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    payload = json.dumps(
        {"hash": head_hash, "key_fingerprint": fingerprint},
        sort_keys=True,
        separators=(",", ":"),
    )
    fd, tmp_name = tempfile.mkstemp(prefix=".pamachain-head-", dir=path.parent)
    try:
        if hasattr(os, "fchmod"):
            os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def _read_anchor() -> dict[str, str] | None:
    path = anchor_path()
    if not path.exists():
        return None
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        head_hash = document["hash"]
        fingerprint = document["key_fingerprint"]
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid ledger anchor") from exc
    if not isinstance(head_hash, str) or not isinstance(fingerprint, str):
        raise ValueError("invalid ledger anchor")
    return {"hash": head_hash, "key_fingerprint": fingerprint}


def _read_blocks(path: Path) -> list[dict]:
    if not path.exists():
        return []
    blocks: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                blocks.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Corrupted ledger record at line {line_number}"
                ) from exc
    return blocks


def append_block(entry: dict) -> dict:
    path = ledger_path()
    with _locked(path, exclusive=True):
        previous_hash = last_hash()
        key = _load_or_create_key()
        fingerprint = _key_fingerprint(key.get_verifying_key())
        anchor = _read_anchor()
        if previous_hash:
            if anchor is None:
                raise ValueError(
                    "ledger anchor is missing; run `pamachain --repair-anchor` "
                    "only after reviewing the ledger"
                )
            if anchor["hash"] != previous_hash:
                raise ValueError(
                    "ledger tail does not match the anchored head; "
                    "refusing to append"
                )
            if anchor["key_fingerprint"] != fingerprint:
                raise ValueError(
                    "ledger signing key does not match the anchored identity"
                )
        elif anchor is not None:
            raise ValueError(
                "ledger is empty but an anchor exists; refusing to append"
            )

        block = dict(entry)
        block["timestamp"] = time.time()
        block["prev_hash"] = previous_hash
        raw = _canonical(block)
        block["hash"] = _hash(raw)
        block["sig"] = key.sign(raw.encode()).hex()

        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with suppress(OSError):
            os.chmod(path, 0o600)
        start = path.stat().st_size if path.exists() else 0
        try:
            flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
            fd = os.open(path, flags, 0o600)
            with os.fdopen(fd, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(block, sort_keys=True) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            _write_anchor(block["hash"], fingerprint)
        except Exception:
            # Do not leave a ledger block that the anchor does not cover.
            with suppress(OSError):
                with path.open("r+", encoding="utf-8") as handle:
                    handle.truncate(start)
                    handle.flush()
                    os.fsync(handle.fileno())
            raise
    return block


def chain(*, verify: bool = True) -> list[dict]:
    path = ledger_path()
    with _locked(path, exclusive=False):
        blocks = _read_blocks(path)
        if verify:
            verify_chain(blocks)
    return blocks


def verify_chain(
    blocks: list[dict] | None = None, *, check_anchor: bool = True
) -> bool:
    """Verify hashes, previous-hash links, signatures, and the anchored head."""
    if blocks is None:
        with _locked(ledger_path(), exclusive=False):
            blocks = _read_blocks(ledger_path())
            return verify_chain(blocks, check_anchor=check_anchor)

    verifying_key = _verifying_key() if blocks else None
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
            raise ValueError(
                f"Ledger block {index} previous-hash verification failed"
            )
        try:
            verifying_key.verify(bytes.fromhex(signature), raw.encode())
        except Exception as exc:
            raise ValueError(
                f"Ledger block {index} signature verification failed"
            ) from exc
        previous_hash = stored_hash

    if check_anchor:
        anchor = _read_anchor()
        if blocks:
            if anchor is None:
                raise ValueError(
                    "ledger anchor is missing; run `pamachain --repair-anchor` "
                    "only after reviewing the ledger"
                )
            if anchor["hash"] != blocks[-1].get("hash"):
                raise ValueError(
                    "ledger tail does not match the anchored head; it may have "
                    "been truncated or rewritten"
                )
            if anchor["key_fingerprint"] != _key_fingerprint(verifying_key):
                raise ValueError(
                    "ledger signing key does not match the anchored identity"
                )
        elif anchor is not None:
            raise ValueError("ledger is empty but an anchor exists; it was deleted")

    return True


def repair_anchor() -> str:
    """Explicitly trust the current ledger and rewrite its head anchor.

    This is intentionally a separate, manual operation: silently repairing a
    missing anchor on every read would defeat truncation detection.
    """
    path = ledger_path()
    with _locked(path, exclusive=True):
        blocks = _read_blocks(path)
        verify_chain(blocks, check_anchor=False)
        if not blocks:
            anchor = anchor_path()
            if anchor.exists():
                anchor.unlink()
            return ""
        verifying_key = _verifying_key()
        head = blocks[-1]["hash"]
        _write_anchor(head, _key_fingerprint(verifying_key))
        return head


def clear_chain() -> None:
    path = ledger_path()
    with _locked(path, exclusive=True):
        for target in (path, anchor_path()):
            if target.exists():
                target.unlink()
