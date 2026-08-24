from app.core.repositories.child_profile import ChildProfileRepo


class ChildProfileService:
    """Работа с профилем ребенка внутри семьи"""

    def __init__(self, repository: ChildProfileRepo):
        self._repo = repository
