from dataclasses import dataclass


@dataclass
class ChildProfile:
    id: int

    name: str
    """Имя профиля внутри семьи"""

    vk_id: str

    family_id: int | None = None

    points_balance: float = 0.0
    """Количество баллов"""
