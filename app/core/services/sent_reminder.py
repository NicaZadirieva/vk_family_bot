from app.core.repositories.sent_reminder import SentReminderRepo


class SentReminderService:
    """Работа над сущностью Напоминание"""

    def __init__(self, repository: SentReminderRepo):
        self._repo = repository
