from __future__ import annotations

from cryptography.fernet import Fernet

from app.config import get_settings


def _get_cipher() -> Fernet:
    settings = get_settings()
    if not settings.fernet_key:
        raise RuntimeError(
            "FERNET_KEY is not set. Generate one with "
            "`python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"`"
        )
    return Fernet(settings.fernet_key.encode() if isinstance(settings.fernet_key, str) else settings.fernet_key)


def encrypt(plaintext: str) -> str:
    return _get_cipher().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    return _get_cipher().decrypt(ciphertext.encode()).decode()
