"""
Argon2id key derivation + AES-256-GCM encryption helpers.
"""
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from argon2.low_level import hash_secret_raw, Type
import base64

def derive_key(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    if salt is None:
        salt = get_random_bytes(16)
    key = hash_secret_raw(
        password.encode(),
        salt,
        time_cost=3,
        memory_cost=64 * 1024,
        parallelism=4,
        hash_len=32,
        type=Type.ID,
    )
    return key, salt

def encrypt(data: bytes, key: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_GCM)
    ct, tag = cipher.encrypt_and_digest(data)
    return cipher.nonce + tag + ct

def decrypt(blob: bytes, key: bytes) -> bytes:
    nonce, tag, ct = blob[:16], blob[16:32], blob[32:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ct, tag)

def encrypt_string(text: str, key: bytes) -> str:
    return base64.b64encode(encrypt(text.encode(), key)).decode()

def decrypt_string(b64: str, key: bytes) -> str:
    return decrypt(base64.b64decode(b64), key).decode()
# --- IGNORE ---
