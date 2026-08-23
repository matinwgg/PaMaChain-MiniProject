"""Small authenticated peer protocol for PaMaChain.

This module deliberately separates transport from ledger validation. Peers exchange
JSON envelopes over any byte-stream transport; callers must validate received blocks
with the ledger's verify_chain() before accepting them.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

MAX_MESSAGE_BYTES = 1_048_576
PROTOCOL_VERSION = 1


@dataclass(frozen=True)
class PeerMessage:
    kind: str
    request_id: str
    payload: dict[str, Any]

    def encode(self) -> bytes:
        body = {"v": PROTOCOL_VERSION, "kind": self.kind, "id": self.request_id, "payload": self.payload}
        encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        if len(encoded) > MAX_MESSAGE_BYTES:
            raise ValueError("peer message exceeds size limit")
        return encoded + b"\n"

    @classmethod
    def decode(cls, raw: bytes) -> "PeerMessage":
        if len(raw) > MAX_MESSAGE_BYTES:
            raise ValueError("peer message exceeds size limit")
        try:
            body = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid peer message") from exc
        if body.get("v") != PROTOCOL_VERSION or not isinstance(body.get("kind"), str):
            raise ValueError("unsupported peer protocol")
        request_id = body.get("id")
        payload = body.get("payload")
        if not isinstance(request_id, str) or not request_id or not isinstance(payload, dict):
            raise ValueError("malformed peer envelope")
        return cls(body["kind"], request_id, payload)


def block_fingerprint(block: dict[str, Any]) -> str:
    """Return a stable identifier for deduplication, not a trust decision."""
    canonical = json.dumps(block, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()


def build_get_chain(request_id: str) -> PeerMessage:
    return PeerMessage("get_chain", request_id, {})


def build_chain_response(request_id: str, blocks: list[dict[str, Any]]) -> PeerMessage:
    return PeerMessage("chain", request_id, {"blocks": blocks})
