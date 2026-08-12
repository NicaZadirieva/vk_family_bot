from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.declarative import declarative_base

from app.core.db.models.base import Base
from app.core.db.models.event_type import EventType


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    family_id = Column(ForeignKey("family.id"), nullable=True)
    title = Column(String(255), nullable=False)
    event_type = Column(Enum(EventType), nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    all_day = Column(Boolean, default=False)

    # recurrence_rule может хранить:
    # {"frequency": "weekly", "days": [0, 2, 4], "interval": 1, "until": "2024-12-31"}
    # или
    # {"frequency": "monthly", "day": 15, "interval": 1, "until": "2024-12-31"}
    recurrence_rule = Column(JSON, nullable=True)

    child_profile_id = Column(Integer, ForeignKey("child_profiles.id"), nullable=True)

    # reminder_deltas: ["-1 day", "-30 minutes"]
    # или [{"days": 1}, {"minutes": 30}] в зависимости от формата
    reminder_deltas = Column(JSON, nullable=True)

    created_by = Column(Integer, nullable=False)  # vk_id
    deleted_at = Column(DateTime, nullable=True)

    # Связь с моделью ChildProfile (если она есть)
    # child_profile = relationship("ChildProfile", back_populates="events")

    def __repr__(self):
        return (
            f"<Event(id={self.id}, title='{self.title}', type={self.event_type.value})>"
        )
