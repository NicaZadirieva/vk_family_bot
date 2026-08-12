from sqlalchemy.ext.asyncio import AsyncSession


class UserRepo:
    """Работа над сущностью User (родитель/ребенок)"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
