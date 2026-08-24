from app.core.repositories.event import EventRepo


class EventService:
    """Обрабатывает события (birthday/lesson/meeting/vacation)"""

    def __init__(self, repository: EventRepo):
        self._repo = repository
