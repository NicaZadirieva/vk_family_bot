from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.entities.base import Base
from app.database.entities.user_role import UserRole


class User(Base):
    """Модель пользователя системы.

    Хранит информацию о пользователях, включая данные из VK,
    роли и привязки к семейному аккаунту.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    """Уникальный идентификатор пользователя в системе."""

    vk_id: Mapped[int | None] = mapped_column(default=None)
    """Уникальный идентификатор пользователя ВКонтакте.

    Может быть None, если пользователь зарегистрирован не через VK.
    """

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), nullable=False
    )
    """Роль пользователя в системе.

    Определяет доступные функции и права.
    Возможные значения: родитель (parent) или ребенок (child).
    """

    username: Mapped[str] = mapped_column(String(80), nullable=False)
    """Полное имя пользователя (ФИО), полученное из VK."""

    timezone: Mapped[str] = mapped_column(String(100), default="Москва +3")
    """Часовой пояс пользователя.

    По умолчанию используется московское время (UTC+3).
    Формат: название города и смещение (например, "Москва +3").
    """

    family_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("family.id"), nullable=False
    )
    """Идентификатор семьи, к которой принадлежит пользователь.

    Внешний ключ к таблице family.
    """

    child_profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("child_profile.id"), nullable=True
    )
    """Идентификатор профиля ребенка.

    Заполняется только для пользователей с ролью 'child'.
    Ссылается на таблицу child_profile.
    Для родителей всегда равен None.
    """
