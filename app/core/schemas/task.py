from dataclasses import dataclass
from datetime import datetime

from app.core.schemas.task_status import TaskStatus


@dataclass
class Task:
    id: int
    family_id: int
    assignee_user_id: int
    """Исполнитель задачи (user.id)"""
    description: str
    """Описание задачи"""
    due_datetime: datetime | None = None
    """Конкретный срок выполнения. NULL - задача без срока"""
    points: int = 0
    """Количество баллов"""
    status: TaskStatus = TaskStatus.ACTIVE
    completed_at: datetime | None = None
    completed_by: int | None = None
    """Кто из родителей подтвердил завершение (user.id)"""
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
