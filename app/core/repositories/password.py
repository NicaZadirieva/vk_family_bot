from sqlalchemy.ext.asyncio import AsyncSession


class PasswordRepo:
    """Работа над сущностью пароль. Нужна для команды /join"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
