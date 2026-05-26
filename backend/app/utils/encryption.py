from cryptography.fernet import Fernet

from app.core.config import settings


def get_fernet() -> Fernet:
    """Get a Fernet instance using the configured encryption key."""
    key = settings.encryption_key
    if not key:
        raise ValueError("ENCRYPTION_KEY is not configured")
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_secret(plaintext: str) -> str:
    """Encrypt a secret (OTP key or NAS shared secret)."""
    f = get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt_secret(ciphertext: str) -> str:
    """Decrypt a previously encrypted secret."""
    f = get_fernet()
    return f.decrypt(ciphertext.encode()).decode()
