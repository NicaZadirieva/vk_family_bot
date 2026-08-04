import logging

from app.database.repositories.password_repository import PasswordRepository
from app.database.repositories.user_repository import UserRepository
from app.errors.invalid_login_error import InvalidLoginError

logger = logging.getLogger(__name__)


class LoginService:
    def __init__(self, password_repo: PasswordRepository, user_repo: UserRepository):
        self._password_repo = password_repo
        self._user_repo = user_repo

    async def search_register_user(self, vk_id: int, family_id: int):
        user = await self._user_repo.search_user(vk_id, family_id)
        return user

    async def is_user_allowed(self, vk_id: int, family_id: int) -> bool:
        tmp_user = await self._user_repo.search_user(vk_id, family_id)
        if not tmp_user:
            raise InvalidLoginError(
                "Юзер не зарегестрирован в системе",
                {"vk_id": vk_id, "family_id": family_id},
            )

        # пользователь существует среди семьи
        logger.info(
            f"Попытка входа под юзером: user_id = {tmp_user.id}, vk_id = {tmp_user.vk_id}, семья = {family_id}"
        )
        is_user_registered = await self._password_repo.search_register_user(
            tmp_user.id, family_id
        )
        if is_user_registered:
            # можно войти в чат через join. пользователь зарегестрирован
            return True
        else:
            raise InvalidLoginError(
                "Попытка входа через юзера без прав",
                {"vk_id": vk_id, "family_id": family_id, "user_id": tmp_user.id},
            )
