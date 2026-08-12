from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.core.db.models.base import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, autoincrement=True)

    family_id = Column(ForeignKey("family.id"), nullable=False)

    title = Column(String(255), nullable=False)

    content = Column(Text, nullable=False)  # Markdown текст

    is_checklist = Column(Boolean, default=False)

    created_by = Column(ForeignKey("user.id"), nullable=False)

    created_at = Column(DateTime, server_default=func.now())

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    can_read_by_all = Column(Boolean, default=True)

    deleted_at = Column(DateTime, nullable=True)
    """Дата удаления (мягкое удаление)"""
