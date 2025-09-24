from pamachain.crypto import derive_key, encrypt, decrypt

def test_encrypt_decrypt():
    key, _ = derive_key("password")
    data = b"hello"
    blob = encrypt(data, key)
    assert decrypt(blob, key) == data
    assert decrypt(blob, key) != b"wrong"
# --- IGNORE ---