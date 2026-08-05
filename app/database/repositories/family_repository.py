from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.entities.family import Family


class FamilyRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.model = Family

    async def search_family_by_link(self, link: str):
        """Поиск семьи по ссылке VK (диалог)"""
        stmt = select(self.model).where(self.model.link == link)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()
