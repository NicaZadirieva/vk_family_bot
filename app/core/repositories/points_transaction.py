from sqlalchemy.ext.asyncio import AsyncSession


class PointsTransactionRepo:
    """Работа над обменом баллами между родитель->ребенок"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
