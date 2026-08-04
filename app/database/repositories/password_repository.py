from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.entities.auth_users import AuthUsers
from app.database.entities.user import User
from app.database.entities.user_role import UserRole


class PasswordRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.model = AuthUsers

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

    async def get_hash(self, user: User):
        stmt = select(self.model.password_hash).where(
            self.model.family_id == user.family_id, self.model.user_id == user.id
        )
        result = await self.db_session.execute(stmt)
        password_hash = result.scalar_one_or_none()
        return password_hash
