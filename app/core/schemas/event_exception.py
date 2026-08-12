from datetime import datetime


class EventException:
    id: int

    event_id: int

    original_date: datetime
    """Оригинальная дата события"""

    new_start_datetime: datetime
    """Новое время для старта события"""

    new_end_datetime: datetime
    """Новое время для конца события"""
