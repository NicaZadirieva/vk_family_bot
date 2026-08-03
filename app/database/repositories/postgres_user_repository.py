from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.user_repository_interface import IUserRepository


class PostgresUserRepository(IUserRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        # self.model = User

    # TODO: реализовать метод поиска юзера
    async def search_user(self, user_id: int, family_id: int):
        pass
