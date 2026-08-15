import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.models.family import Family
from app.core.repositories.base import BaseRepo
from app.exceptions.database_error import DatabaseError

logger = logging.getLogger(__name__)


class FamilyRepo(BaseRepo):
    """Работа над сущностью Семья"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.model = Family

    async def get_family_by_link(self, link: str) -> list[Family]:
        """Получение семьи по ссылке"""
        stmt = select(self.model).where(self.model.link == link)
        result = await self.db_session.execute(stmt)
        return list(result.scalars().all())

    async def create_family(self, name: str, link: str) -> Family:
        """
        Создание новой семьи.

        Args:
            name: Название семьи
            link: Уникальная ссылка

        Returns:
            Family: Созданная семья
        """
        try:
            family = self.model(
                name=name,
                link=link,
                is_active=True,
                created_at=datetime.now(UTC),
            )
            self.db_session.add(family)
            await self.db_session.commit()
            await self.db_session.refresh(family)
            return family

        except Exception as e:
            await self._safe_rollback()
            logger.error(f"Ошибка создания семьи {link}: {e}")
            raise DatabaseError(message="Ошибка создания семьи", details={"link": link})
