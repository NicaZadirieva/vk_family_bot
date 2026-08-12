from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.sql import func

from app.core.db.models.base import Base
from app.core.db.models.reminder_type import ReminderType


class SentReminder(Base):
    __tablename__ = "sent_reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    reminder_type = Column(Enum(ReminderType), nullable=False)
    user_vk_id = Column(Integer, nullable=False, index=True)
    sent_at = Column(DateTime, server_default=func.now())
    delivered = Column(Boolean, default=True)  # TODO: Доставлено ли
    error_message = Column(String(255), nullable=True)  # Ошибка при отправке
    deleted_at = Column(DateTime, nullable=True)
