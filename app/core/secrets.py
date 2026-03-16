from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet


def _fernet(secret_key: str) -> Fernet:
    digest = hashlib.sha256(secret_key.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_secret(value: str, secret_key: str) -> str:
    return _fernet(secret_key).encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_secret(value: str, secret_key: str) -> str:
    return _fernet(secret_key).decrypt(value.encode("utf-8")).decode("utf-8")
