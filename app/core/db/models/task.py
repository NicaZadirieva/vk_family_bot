from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.sql import func

from app.core.db.models.base import Base
from app.core.db.models.task_status import TaskStatus


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    family_id = Column(Integer, nullable=False, index=True)

    assignee_user_id = Column(ForeignKey("user.id"), nullable=False, index=True)
    """Исполнитель задачи (user.id)"""

    description = Column(Text, nullable=False)
    """Описание задачи"""

    due_datetime = Column(DateTime, nullable=True)  # NULL - задача без срока
    """Конкретный срок выполнения """

    points = Column(Integer, default=0)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.ACTIVE)
    completed_at = Column(DateTime, nullable=True)

    completed_by = Column(ForeignKey("user.id"), nullable=True)
    """Кто из родителей подтвердил завершение """

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
