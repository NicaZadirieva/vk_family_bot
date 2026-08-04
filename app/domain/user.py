from dataclasses import dataclass

from app.domain.user_role import UserRole


@dataclass
class User:
    """
    Роль юзера (родитель/ребенок)
    """

    role: UserRole

    """
    ФИО юзера, как в VK
    """
    username: str

    family_id: int

    """
    Часовой пояс (по умолчанию – Москва +3)
    """
    timezone: str = "Москва +3"

    """
    Уникальный идентификатор ВКонтакте
    """
    vk_id: int | None = None

    child_profile_id: int | None = None
