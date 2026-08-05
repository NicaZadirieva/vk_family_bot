from dataclasses import dataclass
from datetime import datetime


@dataclass
class Family:
    id: int

    name: str
    """
    Название семьи (Например, общая фамилия)
    """
    link: str
    """
    Ссылка VK на чат с семьей
    """
    created_at: datetime
