from app.core.repositories.user import UserRepo


class UserService:
    """Работа над сущностью User (родитель/ребенок)"""

    def __init__(self, repo: UserRepo):
        self._repo = repo
