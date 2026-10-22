"""Filesystem locations for PaMaChain state.

Every path can be overridden with an environment variable. Tests must set
``PAMACHAIN_LEDGER``, ``PAMACHAIN_LEDGER_KEY``, ``PAMACHAIN_LEDGER_ANCHOR`` and
``PAMACHAIN_KEYSTORE`` to a temporary directory so they never touch the real
user's vault.
"""

from __future__ import annotations

import os
from pathlib import Path


def _path_from_env(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    return Path(value).expanduser() if value else default


def ledger_path() -> Path:
    return _path_from_env(
        "PAMACHAIN_LEDGER", Path.home() / ".pamachain_ledger.jsonl"
    )


def signing_key_path() -> Path:
    return _path_from_env(
        "PAMACHAIN_LEDGER_KEY",
        Path.home() / ".pamachain_ledger_signing_key.pem",
    )


def anchor_path() -> Path:
    return _path_from_env(
        "PAMACHAIN_LEDGER_ANCHOR",
        Path.home() / ".pamachain_ledger.head.json",
    )


def keystore_path() -> Path:
    return _path_from_env(
        "PAMACHAIN_KEYSTORE", Path.home() / ".pamachain_keystore.json"
    )


def lock_path(path: Path) -> Path:
    return path.with_name(path.name + ".lock")
