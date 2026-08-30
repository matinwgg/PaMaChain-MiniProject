import pytest

from pamachain.crypto import decrypt, derive_key, encrypt, decrypt_string, encrypt_string


def test_encrypt_decrypt_round_trip() -> None:
    key, salt = derive_key("correct horse battery staple")
    assert len(key) == 32
    assert len(salt) == 16
    plaintext = b"hello PaMaChain"
    assert decrypt(encrypt(plaintext, key), key) == plaintext


def test_wrong_key_fails_authentication() -> None:
    key, _ = derive_key("password-a")
    wrong_key, _ = derive_key("password-b")
    with pytest.raises(ValueError, match="failed authentication"):
        decrypt(encrypt(b"secret", key), wrong_key)


def test_tampering_fails_authentication() -> None:
    key, _ = derive_key("password")
    blob = bytearray(encrypt(b"secret", key))
    blob[-1] ^= 1
    with pytest.raises(ValueError, match="failed authentication"):
        decrypt(bytes(blob), key)


def test_truncated_payload_is_rejected() -> None:
    key, _ = derive_key("password")
    with pytest.raises(ValueError, match="truncated"):
        decrypt(b"too-short", key)


def test_string_round_trip_and_invalid_base64() -> None:
    key, _ = derive_key("password")
    encoded = encrypt_string("π chain", key)
    assert decrypt_string(encoded, key) == "π chain"
    with pytest.raises(ValueError, match="base64"):
        decrypt_string("not!base64", key)


def test_invalid_key_and_salt_sizes_are_rejected() -> None:
    with pytest.raises(ValueError, match="salt"):
        derive_key("password", b"short")
    with pytest.raises(ValueError, match="key"):
        encrypt(b"data", b"short")
