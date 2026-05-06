import hmac
import hashlib

VERSION_BYTE = b'\x01'

def wrap_payload(ciphertext: bytes, key: bytes) -> bytes:
    """Wrap ciphertext in an envelope with version byte and HMAC."""
    h = hmac.new(key, ciphertext, hashlib.sha256)
    return VERSION_BYTE + h.digest() + ciphertext

def unwrap_payload(payload: bytes, key: bytes) -> bytes:
    """Unwrap payload, verify HMAC and return ciphertext. Raises ValueError if tampered."""
    if payload[0:1] != VERSION_BYTE:
        raise ValueError("Invalid version byte")
    
    provided_mac = payload[1:33]
    ciphertext = payload[33:]
    
    h = hmac.new(key, ciphertext, hashlib.sha256)
    if not hmac.compare_digest(provided_mac, h.digest()):
        raise ValueError("HMAC verification failed, payload tampered")
        
    return ciphertext
