import logging
from dataclasses import dataclass
from enum import Enum

from passlib.context import CryptContext

from app.database.repositories.password_repository import PasswordRepository


class VerificationResult(Enum):
    """Результат верификации пароля."""

    SUCCESS = "success"
    USER_NOT_FOUND = "user_not_found"
    INVALID_PASSWORD = "invalid_password"
    NEEDS_REHASH = "needs_rehash"
    INTERNAL_ERROR = "internal_error"


@dataclass
class PasswordVerification:
    """Результат проверки пароля."""

    result: VerificationResult
    needs_rehash: bool = False
    user_id: int | None = None


logger = logging.getLogger(__name__)


class PasswordService:
    def __init__(self, password_repo: PasswordRepository):
        self._password_repo = password_repo
        self._pwd_context = CryptContext(
            schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12
        )

    async def verify_user(
        self, user_id: int, vk_id: int, family_id: int, password: str
    ) -> PasswordVerification:
        """
        Проверяет пароль пользователя.

        Returns:
            PasswordVerification: Результат проверки
        """
        try:
            stored_hash = await self._password_repo.get_hash(user_id, vk_id, family_id)

            if not stored_hash:
                return PasswordVerification(result=VerificationResult.USER_NOT_FOUND)

            is_valid = self._pwd_context.verify(password, stored_hash)

            if not is_valid:
                return PasswordVerification(result=VerificationResult.INVALID_PASSWORD)

            # Проверяем, нужно ли перехешировать
            needs_rehash = self._pwd_context.needs_update(stored_hash)

            return PasswordVerification(
                result=VerificationResult.SUCCESS,
                needs_rehash=needs_rehash,
                user_id=user_id,
            )

        except Exception as e:
            logger.error(f"Password verification error: {e}", exc_info=True)
            return PasswordVerification(result=VerificationResult.INTERNAL_ERROR)
