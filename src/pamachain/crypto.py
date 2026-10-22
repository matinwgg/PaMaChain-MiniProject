"""Cryptographic primitives used by the PaMaChain educational wallet.

The module deliberately delegates cryptographic operations to PyCryptodome and
Argon2 rather than implementing primitives from scratch. It is not a protocol
specification or a production wallet implementation.
"""
from __future__ import annotations

import base64
import binascii
import hmac

# PyCryptodome intentionally uses the historical ``Crypto`` namespace. Bandit's
# B413 rule matches that name and mistakes it for the abandoned pycrypto package.
from Crypto.Cipher import AES  # nosec B413
from Crypto.Random import get_random_bytes  # nosec B413
from argon2.low_level import Type, hash_secret_raw

_SALT_SIZE = 16
_KEY_SIZE = 32
_NONCE_SIZE = 16
_TAG_SIZE = 16


def derive_key(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    """Derive a 256-bit key from a password using Argon2id."""
    if not isinstance(password, str) or not password:
        raise ValueError("password must be a non-empty string")
    if salt is None:
        salt = get_random_bytes(_SALT_SIZE)
    if len(salt) != _SALT_SIZE:
        raise ValueError("salt must be exactly 16 bytes")

    key = hash_secret_raw(
        password.encode("utf-8"),
        salt,
        time_cost=3,
        memory_cost=64 * 1024,
        parallelism=4,
        hash_len=_KEY_SIZE,
        type=Type.ID,
    )
    return key, salt


def encrypt(data: bytes, key: bytes) -> bytes:
    """Encrypt bytes with AES-256-GCM.

    Format: nonce || authentication_tag || ciphertext.
    """
    if len(key) != _KEY_SIZE:
        raise ValueError("key must be exactly 32 bytes")
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")

    cipher = AES.new(key, AES.MODE_GCM, nonce=get_random_bytes(_NONCE_SIZE))
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return cipher.nonce + tag + ciphertext


def decrypt(blob: bytes, key: bytes) -> bytes:
    """Decrypt and authenticate an AES-GCM payload.

    Invalid, truncated, or tampered payloads fail closed with ``ValueError``.
    """
    if len(key) != _KEY_SIZE:
        raise ValueError("key must be exactly 32 bytes")
    if len(blob) < _NONCE_SIZE + _TAG_SIZE:
        raise ValueError("encrypted payload is truncated")

    nonce = blob[:_NONCE_SIZE]
    tag = blob[_NONCE_SIZE : _NONCE_SIZE + _TAG_SIZE]
    ciphertext = blob[_NONCE_SIZE + _TAG_SIZE :]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    try:
        return cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError as exc:
        raise ValueError("encrypted payload failed authentication") from exc


def encrypt_string(text: str, key: bytes) -> str:
    """Encrypt UTF-8 text and return a base64 representation."""
    return base64.b64encode(encrypt(text.encode("utf-8"), key)).decode("ascii")


def decrypt_string(encoded: str, key: bytes) -> str:
    """Decode and decrypt a base64 AES-GCM payload."""
    try:
        blob = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("encrypted value is not valid base64") from exc
    return decrypt(blob, key).decode("utf-8")


# A verifier lets the keystore prove that a supplied master password derives the
# same key used when the vault was created. Only the authenticated ciphertext is
# stored; the plaintext marker below is public and not a secret.
VERIFIER_TEXT = "pamachain-keystore-verifier-v1"


def make_verifier(key: bytes) -> str:
    """Return a password-check value that is safe to store next to the salt."""
    if len(key) != _KEY_SIZE:
        raise ValueError("key must be exactly 32 bytes")
    return encrypt_string(VERIFIER_TEXT, key)


def verify_key(key: bytes, verifier: str) -> bool:
    """Return True when ``key`` is the key that created ``verifier``."""
    if not isinstance(verifier, str) or not verifier:
        return False
    if len(key) != _KEY_SIZE:
        return False
    try:
        return hmac.compare_digest(decrypt_string(verifier, key), VERIFIER_TEXT)
    except ValueError:
        return False
