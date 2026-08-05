from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.entities.base import Base


class Family(Base):
    __tablename__ = "family"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(20), nullable=False)
    """
    Название семьи (Например, общая фамилия)
    """
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    link: Mapped[str] = mapped_column(String(50), nullable=True)
    """
    Ссылка VK на чат с семьей
    """
