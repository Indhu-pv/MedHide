from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64, os

HOSPITAL_SALT = os.environ.get('HOSPITAL_SALT', 'medhide_default_salt').encode()

def derive_key(mrd_number: str, uid: str = None) -> bytes:
    """Derive 256-bit AES key from patient MRD + hospital salt + optional UID."""
    # Combine mrd and uid if uid is provided
    material = mrd_number if uid is None else f"{mrd_number}:{uid}"
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,            # 256 bits
        salt=HOSPITAL_SALT,
        iterations=600_000,   # OWASP 2024 recommendation
    )
    return kdf.derive(material.encode())
