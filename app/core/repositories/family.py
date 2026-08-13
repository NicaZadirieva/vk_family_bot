from sqlalchemy.ext.asyncio import AsyncSession


class FamilyRepo:
    """Работа над сущностью Семья"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
