from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.join_context import JoinContext
from app.database.entities.auth_users import AuthUsers
from app.database.entities.user import User
from app.database.entities.user_role import UserRole


class PasswordRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.model = AuthUsers

    # TODO: нужен ли vk_id для поиска
    async def get_hash(self, user_id: int, vk_id: int, family_id: int):
        stmt = select(self.model.password_hash).where(
            self.model.family_id == family_id, self.model.user_id == user_id
        )
        result = await self.db_session.execute(stmt)
        password_hash = result.scalar_one_or_none()
        return password_hash
