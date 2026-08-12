from sqlalchemy.ext.asyncio import AsyncSession


class NoteRepo:
    """Работа над сущностью Заметка"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
