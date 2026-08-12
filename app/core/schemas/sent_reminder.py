from dataclasses import dataclass
from datetime import datetime

from app.core.schemas.reminder_type import ReminderType


@dataclass
class SentReminder:
    """Модель отправленного напоминания"""

    id: int
    reminder_type: ReminderType
    user_vk_id: int
    sent_at: datetime
    task_id: int | None = None
    event_id: int | None = None
    delivered: bool = True
    error_message: str | None = None
    deleted_at: datetime | None = None
