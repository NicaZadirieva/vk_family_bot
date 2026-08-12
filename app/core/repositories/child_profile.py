from sqlalchemy.ext.asyncio import AsyncSession


class ChildProfileRepo:
    """Работа с профилем ребенка внутри семьи"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
