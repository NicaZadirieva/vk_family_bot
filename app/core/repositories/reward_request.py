from sqlalchemy.ext.asyncio import AsyncSession


class RewardRequestRepo:
    """Запрашивает разрешение родителя на покупку награды для ребенка"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
