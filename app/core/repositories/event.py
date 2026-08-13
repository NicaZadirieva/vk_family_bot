from sqlalchemy.ext.asyncio import AsyncSession


class EventRepo:
    """Обрабатывает события (birthday/lesson/meeting/vacation)"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
