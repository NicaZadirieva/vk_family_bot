from passlib.context import CryptContext

from app.core.mapper import Mapper
from app.database.repositories.password_repository import PasswordRepository
from app.domain.user import User
from app.errors.not_found_user import NotFoundError

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

    async def verify_user(self, user: User, plain_password: str):
        userDb = Mapper.to_userDb(user)
        hash: str | None = await self._password_repo.get_hash(userDb)
        if not hash:
            raise NotFoundError(
                "Пользователь с текущими данными не найден для верификации",
                {"user_id": user.id, "vk_id": user.vk_id, "family_id": user.family_id},
            )

        return PasswordService.verify(plain_password, hash)
