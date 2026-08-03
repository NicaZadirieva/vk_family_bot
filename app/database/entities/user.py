from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.entities.base import Base
from app.database.entities.role import UserRole


class User(Base):
    __tablename__ = "users"

    """
    Уникальный идентификатор ВКонтакте
    """
    vk_id: Mapped[int | None] = mapped_column(default=None)

    """
    Роль юзера (родитель/ребенок)
    """
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), nullable=False
    )

    """
    ФИО юзера, как в VK
    """
    username: Mapped[String] = mapped_column(String(80), nullable=False)

    """
    Часовой пояс (по умолчанию – Москва +3)
    """
    timezone: Mapped[str] = mapped_column(String(100), default="Москва +3")

    family_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("family.id"), nullable=False
    )
    child_profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("child_profile.id"), nullable=True
    )
