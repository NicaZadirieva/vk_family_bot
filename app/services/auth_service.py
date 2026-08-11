from dataclasses import dataclass

from app.core.mapper import Mapper
from app.database.repositories.password_repository import PasswordRepository
from app.services.session_service import SessionRepository, SessionService
from app.database.repositories.user_repository import UserRepository
from app.domain.user import User
from app.services.password_service import PasswordService


@dataclass
class AuthResult:
    success: bool
    user: User | None = None
    error_code: str | None = None
    error_details: dict | None = None


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        password_service: PasswordService,
        session_service: SessionService,
    ):
        self._user_repo = user_repo
        self._password_service = password_service
        self._session_service = session_service

    async def authenticate_with_password(
        self, vk_id: int, family_id: int, password: str
    ) -> AuthResult:
        """Аутентификация с проверкой пароля."""
        user = await self._user_repo.search_user(vk_id, family_id)
        if not user:
            return AuthResult(success=False, error_code="USER_NOT_FOUND")

        # Проверка пароля
        is_valid = await self._password_service.verify_user(
            user_id=user.id, family_id=family_id, vk_id=vk_id, password=password
        )

        if not is_valid:
            return AuthResult(success=False, error_code="INVALID_PASSWORD")

        # Обновление сессии
        await self._session_service.start_new_session(user.id)

        return AuthResult(success=True, user=Mapper.to_userDTO(user))
