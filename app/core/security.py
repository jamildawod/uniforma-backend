from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass(frozen=True)
class TokenPayload:
    subject: str | None
    token_type: str | None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _create_token(
    subject: str,
    expires_delta: timedelta,
    secret_key: str,
    token_type: str,
) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(
        payload,
        secret_key,
        algorithm=get_settings().jwt_algorithm,
    )


def create_access_token(subject: str) -> str:
    settings = get_settings()
    return _create_token(
        subject=subject,
        expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes),
        secret_key=settings.jwt_secret_key,
        token_type="access",
    )


def create_refresh_token(subject: str) -> str:
    settings = get_settings()
    return _create_token(
        subject=subject,
        expires_delta=timedelta(minutes=settings.jwt_refresh_token_expire_minutes),
        secret_key=settings.jwt_refresh_secret_key,
        token_type="refresh",
    )


def decode_token(token: str) -> TokenPayload:
    settings = get_settings()
    decoded: dict[str, Any] | None = None

    for secret in (settings.jwt_secret_key, settings.jwt_refresh_secret_key):
        try:
            decoded = jwt.decode(
                token,
                secret,
                algorithms=[settings.jwt_algorithm],
            )
            break
        except jwt.InvalidTokenError:
            continue

    if decoded is None:
        return TokenPayload(subject=None, token_type=None)

    return TokenPayload(
        subject=decoded.get("sub"),
        token_type=decoded.get("type"),
    )
