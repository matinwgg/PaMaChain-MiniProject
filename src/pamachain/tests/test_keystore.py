import os

import pytest

from pamachain.crypto import derive_key, make_verifier, verify_key
from pamachain.keystore import (
    load_keystore,
    load_salt,
    save_keystore,
    save_salt,
)


@pytest.fixture
def keystore_env(tmp_path, monkeypatch):
    monkeypatch.setenv("PAMACHAIN_KEYSTORE", str(tmp_path / "keystore.json"))
    return tmp_path


def test_round_trip(keystore_env):
    key, salt = derive_key("correct horse battery staple")
    save_keystore(salt, make_verifier(key))

    document = load_keystore()
    assert document is not None
    assert document["salt"] == salt
    assert verify_key(key, document["verifier"])


def test_wrong_password_is_rejected(keystore_env):
    key, salt = derive_key("password-a")
    save_keystore(salt, make_verifier(key))

    wrong_key, _ = derive_key("password-b", salt)
    assert not verify_key(wrong_key, load_keystore()["verifier"])


def test_legacy_salt_only_keystore(keystore_env):
    _, salt = derive_key("password")
    save_salt(salt)

    document = load_keystore()
    assert document == {"salt": salt, "verifier": None}
    assert load_salt() == salt


def test_invalid_keystore_is_rejected(keystore_env):
    (keystore_env / "keystore.json").write_text("not json", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid PaMaChain keystore"):
        load_keystore()


def test_verifier_tampering_is_rejected(keystore_env):
    key, _ = derive_key("password")
    verifier = make_verifier(key)
    replacement = "A" if verifier[0] != "A" else "B"
    assert not verify_key(key, replacement + verifier[1:])


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits")
def test_keystore_is_owner_only(keystore_env):
    key, salt = derive_key("password")
    save_keystore(salt, make_verifier(key))
    mode = (keystore_env / "keystore.json").stat().st_mode
    assert mode & 0o077 == 0
