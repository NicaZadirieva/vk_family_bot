from app.core.repositories.event_exception import EventExceptionRepo


class EventExceptionService:
    """Исключает в процессе напоминания конкретный event"""

    def __init__(self, repo: EventExceptionRepo):
        self._repo = repo
