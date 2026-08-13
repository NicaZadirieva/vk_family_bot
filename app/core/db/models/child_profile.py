from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.models.base import Base


class ChildProfile(Base):
    __tablename__ = "child_profile"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    """Имя профиля внутри семьи"""

    vk_id: Mapped[str] = mapped_column(String(100), nullable=True)

    family_id: Mapped[int] = mapped_column(ForeignKey("family.id"), nullable=True)

    points_balance: Mapped[float] = mapped_column(Integer, default=0.0)
    """Количество баллов"""
