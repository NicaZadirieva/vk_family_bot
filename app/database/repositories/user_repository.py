from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.entities.user import User


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.model = User

    async def search_user(self, vk_id: int, family_id: int):
        """Поиск юзера по VK Id внутри семьи (family_id)"""
        stmt = select(self.model).where(
            self.model.vk_id == vk_id, self.model.family_id == family_id
        )
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()
