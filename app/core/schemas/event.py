from dataclasses import dataclass
from datetime import datetime
from typing import Any

from pydantic import Field

from app.core.schemas.event_type import EventType


@dataclass
class Event:
    id: int
    family_id: int
    event_type: EventType

    start_datetime: datetime
    """Старт события"""

    end_datetime: datetime
    """Конец события"""

    created_by: int
    """vk_id создавшего событие"""

    title: str = Field(..., min_length=1, max_length=255)
    """Название события"""

    # recurrence_rule может хранить:
    # {"frequency": "weekly", "days": [0, 2, 4], "interval": 1, "until": "2024-12-31"}
    # или
    # {"frequency": "monthly", "day": 15, "interval": 1, "until": "2024-12-31"}
    recurrence_rule: dict[str, Any] | None = None
    """дни недели, период действия"""

    child_profile_id: int | None = None

    reminder_deltas: list[str] | None = None
    """JSON, например, [-1 day, -30 minutes]"""

    all_day: bool = False
    """Длится весь день без привязки к конкретному часу?"""

    deleted_at: datetime | None = None
