from app.database.repositories.user_repository_interface import IUserRepository


class UserService:
    def __init__(self, repo: IUserRepository):
        self._repo = repo

    async def is_user_allowed(self, user_id: int, family_id: int) -> bool:
        return True
