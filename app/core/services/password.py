from app.core.repositories.password import PasswordRepo


class PasswordService:
    """Работа над сущностью пароль. Нужна для команды /join"""

    def __init__(self, repository: PasswordRepo):
        self._repo = repository
