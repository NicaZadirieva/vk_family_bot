from sqlalchemy.ext.asyncio import AsyncSession


class TasksRepo:
    """Работа над сущностью Задача"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
