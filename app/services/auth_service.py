from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPair
from app.services.user_service import UserService


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_service = UserService(user_repository)

    async def authenticate_user(self, email: str, password: str) -> TokenPair | None:
        user = await self.user_service.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            return None
        return TokenPair(
            access_token=create_access_token(user.email),
            refresh_token=create_refresh_token(user.email),
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenPair | None:
        payload = decode_token(refresh_token)
        if payload.subject is None or payload.token_type != "refresh":
            return None

        user = await self.user_service.get_by_email(payload.subject)
        if user is None or not user.is_active:
            return None

        return TokenPair(
            access_token=create_access_token(user.email),
            refresh_token=create_refresh_token(user.email),
        )
