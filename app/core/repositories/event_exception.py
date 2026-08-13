from sqlalchemy.ext.asyncio import AsyncSession


class EventExceptionRepo:
    """Исключает в процессе напоминания конкретный event"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
