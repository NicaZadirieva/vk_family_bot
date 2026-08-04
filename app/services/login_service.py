import logging

from app.database.repositories.auth_users_repository import AuthUsersRepository
from app.database.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class LoginService:
    def __init__(self, auth_user_repo: AuthUsersRepository, user_repo: UserRepository):
        self._auth_user_repo = auth_user_repo
        self._user_repo = user_repo

    async def is_user_allowed(self, vk_id: int, family_id: int) -> bool:
        tmp_user = await self._user_repo.search_user(vk_id, family_id)
        if not tmp_user:
            return False

        # пользователь существует среди семьи
        logger.info(
            f"Попытка входа под юзером: user_id = {tmp_user.id}, vk_id = {tmp_user.vk_id}, семья = {family_id}"
        )
        is_user_registered = await self._auth_user_repo.search_register_user(
            tmp_user.id, family_id
        )
        if is_user_registered:
            # можно войти в чат через join. пользователь зарегестрирован
            return True
        else:
            logger.error(
                "Несанкционированный доступ. Попытка входа через юзера без прав"
            )
            return False
