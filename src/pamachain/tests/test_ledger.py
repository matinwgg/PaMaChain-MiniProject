import json
import os

import pytest

from pamachain.ledger.mock_chain import (
    append_block,
    chain,
    clear_chain,
    repair_anchor,
)


@pytest.fixture
def ledger_env(tmp_path, monkeypatch):
    monkeypatch.setenv("PAMACHAIN_LEDGER", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setenv("PAMACHAIN_LEDGER_KEY", str(tmp_path / "key.pem"))
    monkeypatch.setenv("PAMACHAIN_LEDGER_ANCHOR", str(tmp_path / "head.json"))
    return tmp_path


def test_append_chain(ledger_env):
    entry = append_block({"label": "test", "secret": "abc"})
    blocks = chain()
    assert blocks[-1]["hash"] == entry["hash"]
    assert blocks[-1]["label"] == "test"
    assert blocks[-1]["secret"] == "abc"


def test_chain_links_blocks(ledger_env):
    first = append_block({"label": "one"})
    second = append_block({"label": "two"})
    blocks = chain()
    assert len(blocks) == 2
    assert blocks[0]["prev_hash"] == ""
    assert blocks[1]["prev_hash"] == first["hash"]
    assert blocks[1]["hash"] == second["hash"]


def test_tampering_is_detected(ledger_env):
    append_block({"label": "one", "secret": "abc"})
    path = ledger_env / "ledger.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    block = json.loads(lines[-1])
    block["secret"] = "evil"
    lines[-1] = json.dumps(block, sort_keys=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="hash verification failed"):
        chain()


def test_bad_signature_is_detected(ledger_env):
    append_block({"label": "one"})
    path = ledger_env / "ledger.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    block = json.loads(lines[-1])
    block["sig"] = "00" * 64
    lines[-1] = json.dumps(block, sort_keys=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="signature verification failed"):
        chain()


def test_truncation_is_detected(ledger_env):
    append_block({"label": "one"})
    append_block({"label": "two"})
    path = ledger_env / "ledger.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text(lines[0] + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="anchored head"):
        chain()
    with pytest.raises(ValueError, match="refusing to append"):
        append_block({"label": "three"})


def test_missing_anchor_requires_explicit_repair(ledger_env):
    append_block({"label": "one"})
    (ledger_env / "head.json").unlink()

    with pytest.raises(ValueError, match="anchor is missing"):
        chain()
    with pytest.raises(ValueError, match="anchor is missing"):
        append_block({"label": "two"})

    repair_anchor()
    assert chain()[-1]["label"] == "one"
    append_block({"label": "two"})
    assert chain()[-1]["label"] == "two"


def test_deleted_ledger_is_detected(ledger_env):
    append_block({"label": "one"})
    (ledger_env / "ledger.jsonl").unlink()

    with pytest.raises(ValueError, match="ledger is empty but an anchor exists"):
        chain()
    with pytest.raises(ValueError, match="refusing to append"):
        append_block({"label": "two"})


def test_clear_chain(ledger_env):
    append_block({"label": "one"})
    clear_chain()
    assert chain() == []


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits")
def test_state_files_are_owner_only(ledger_env):
    append_block({"label": "one"})
    for name in ("ledger.jsonl", "key.pem", "head.json"):
        assert (ledger_env / name).stat().st_mode & 0o077 == 0, name
