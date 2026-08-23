import pytest

from pamachain import crypto
from pamachain.ledger import mock_chain


def test_encrypt_round_trip_and_wrong_key_detection():
    key, salt = crypto.derive_key("correct horse battery staple")
    assert len(salt) == 16
    blob = crypto.encrypt(b"secret", key)
    assert crypto.decrypt(blob, key) == b"secret"
    with pytest.raises(Exception):
        crypto.decrypt(blob[:-1] + bytes([blob[-1] ^ 1]), key)


def test_encrypted_payload_has_version_and_random_nonce():
    key, _ = crypto.derive_key("password")
    first = crypto.encrypt(b"same", key)
    second = crypto.encrypt(b"same", key)
    assert first[:1] == crypto.FORMAT_VERSION
    assert second[:1] == crypto.FORMAT_VERSION
    assert first != second


def test_ledger_detects_tampering(tmp_path, monkeypatch):
    monkeypatch.setattr(mock_chain, "LEDGER", tmp_path / "ledger.jsonl")
    monkeypatch.setattr(mock_chain, "SIGNING_KEY_FILE", tmp_path / "signing.key")
    mock_chain.append_block({"service": "github", "secret": "encrypted"})
    mock_chain.append_block({"service": "google", "secret": "encrypted"})
    assert mock_chain.verify_chain() is True

    blocks = mock_chain.chain()
    blocks[0]["secret"] = "tampered"
    mock_chain.LEDGER.write_text("\n".join(__import__("json").dumps(b) for b in blocks) + "\n")
    assert mock_chain.verify_chain() is False
