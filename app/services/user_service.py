from app.core.logging import get_logger
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository
        self.logger = get_logger(self.__class__.__name__)

    async def get_by_email(self, email: str) -> User | None:
        return await self.repository.get_by_email(email)

    async def create_user(self, payload: UserCreate, is_superuser: bool = False) -> User:
        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            is_superuser=is_superuser,
            is_active=True,
        )
        created = await self.repository.add(user)
        self.logger.info("Created user account for %s", created.email)
        return created
