"""Cryptographic primitives used by the PaMaChain educational wallet.

The module deliberately delegates cryptographic operations to PyCryptodome and
Argon2 rather than implementing primitives from scratch. It is not a protocol
specification or a production wallet implementation.
"""
from __future__ import annotations

import base64
import binascii

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
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
