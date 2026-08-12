from dataclasses import dataclass
from datetime import datetime


@dataclass
class Note:
    id: int
    family_id: int
    title: str
    content: str  # Markdown текст

    created_by: int
    """ID пользователя, создавшего заметку"""

    created_at: datetime
    updated_at: datetime

    is_checklist: bool = False
    """Флаг: является ли заметка чек-листом"""

    deleted_at: datetime | None = None
    """Дата удаления (мягкое удаление)"""
