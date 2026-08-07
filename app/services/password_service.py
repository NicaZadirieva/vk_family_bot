from passlib.context import CryptContext

from app.core.join_context import JoinContext
from app.database.repositories.password_repository import PasswordRepository
from app.errors.resource_not_found_error import ResourceNotFoundError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordService:
    """Сервис для работы с паролями (Domain Service)"""

    @staticmethod
    def hash(plain_password: str) -> str:
        """Хеширует пароль"""
        return pwd_context.hash(plain_password)

    @staticmethod
    def verify(plain_password: str, password_hash: str) -> bool:
        """Проверяет пароль"""
        return pwd_context.verify(plain_password, password_hash)

    @staticmethod
    def needs_rehash(password_hash: str) -> bool:
        """Проверяет, нужно ли обновить хеш"""
        return pwd_context.needs_update(password_hash)

    def __init__(self, password_repo: PasswordRepository):
        self._password_repo = password_repo

    async def verify_user(self, joinContext: JoinContext):
        hash: str | None = await self._password_repo.get_hash(joinContext)
        if not hash:
            raise ResourceNotFoundError(
                "Пользователь с текущими данными не найден для верификации",
                {
                    "user_id": joinContext.user_id,
                    "vk_id": joinContext.vk_id,
                    "family_id": joinContext.family_id,
                },
            )

        return PasswordService.verify(joinContext.password, hash)
