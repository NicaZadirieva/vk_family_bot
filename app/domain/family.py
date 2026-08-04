from dataclasses import dataclass
from datetime import datetime


@dataclass
class Family:
    id: int
    """
    Название семьи (Например, общая фамилия)
    """
    name: str
    created_at: datetime
