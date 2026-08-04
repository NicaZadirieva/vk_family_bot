from sqlalchemy.ext.asyncio import AsyncSession

from app.database.entities.user import User
from app.database.entities.user_role import UserRole


class AuthUsersRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        # self.model = User

    # TODO: реализовать метод поиска юзера среди зарегестрированных модератором семьи
    async def search_register_user(self, user_id: int, family_id: int):
        # TODO: тестовый юзер
        return User(
            id=1,
            vk_id=2,
            role=UserRole.CHILD,
            username="Ника",
            family_id=1234,
            child_profile_id=344545,
        )
