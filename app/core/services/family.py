from app.core.repositories.family import FamilyRepo


class FamilyService:
    """Работа над сущностью Семья"""

    def __init__(self, repo: FamilyRepo):
        self._repo = repo
