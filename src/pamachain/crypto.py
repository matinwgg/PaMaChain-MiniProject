"""Password-based encryption helpers for PaMaChain."""
import base64

from argon2.low_level import Type, hash_secret_raw
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

FORMAT_VERSION = b"\x01"
SALT_SIZE = 16
NONCE_SIZE = 12
TAG_SIZE = 16
KEY_SIZE = 32


def derive_key(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string")
    salt = salt or get_random_bytes(SALT_SIZE)
    if len(salt) != SALT_SIZE:
        raise ValueError("Salt must be exactly 16 bytes")
    key = hash_secret_raw(password.encode("utf-8"), salt, time_cost=3, memory_cost=64 * 1024, parallelism=4, hash_len=KEY_SIZE, type=Type.ID)
    return key, salt


def encrypt(data: bytes, key: bytes) -> bytes:
    if len(key) != KEY_SIZE:
        raise ValueError("AES-256 requires a 32-byte key")
    cipher = AES.new(key, AES.MODE_GCM, nonce=get_random_bytes(NONCE_SIZE))
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return FORMAT_VERSION + cipher.nonce + tag + ciphertext


def decrypt(blob: bytes, key: bytes) -> bytes:
    if len(key) != KEY_SIZE:
        raise ValueError("AES-256 requires a 32-byte key")
    if len(blob) < 1 + NONCE_SIZE + TAG_SIZE or blob[:1] != FORMAT_VERSION:
        raise ValueError("Invalid or unsupported encrypted payload")
    nonce = blob[1:1 + NONCE_SIZE]
    tag = blob[1 + NONCE_SIZE:1 + NONCE_SIZE + TAG_SIZE]
    ciphertext = blob[1 + NONCE_SIZE + TAG_SIZE:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)


def encrypt_string(text: str, key: bytes) -> str:
    return base64.b64encode(encrypt(text.encode("utf-8"), key)).decode("ascii")


def decrypt_string(encoded: str, key: bytes) -> str:
    try:
        blob = base64.b64decode(encoded.encode("ascii"), validate=True)
    except Exception as exc:
        raise ValueError("Invalid encrypted text encoding") from exc
    return decrypt(blob, key).decode("utf-8")
