from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.models.base import Base


class EventException(Base):
    __tablename__ = "event_exception"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), nullable=False)

    original_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    """Оригинальная дата события"""

    new_start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    """Новое время для старта события"""

    new_end_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    """Новое время для конца события"""
