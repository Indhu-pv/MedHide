from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def encrypt(plaintext: bytes, key: bytes) -> bytes:
    """Encrypt with AES-256-GCM. Returns iv + tag + ciphertext."""
    aesgcm = AESGCM(key)  # key must be 32 bytes
    iv = os.urandom(12)   # 96-bit nonce
    ciphertext = aesgcm.encrypt(iv, plaintext, None)
    return iv + ciphertext  # GCM appends 16-byte tag to ciphertext

def decrypt(payload: bytes, key: bytes) -> bytes:
    """Decrypt AES-256-GCM payload. Raises InvalidTag if tampered."""
    aesgcm = AESGCM(key)
    iv, ciphertext = payload[:12], payload[12:]
    return aesgcm.decrypt(iv, ciphertext, None)
