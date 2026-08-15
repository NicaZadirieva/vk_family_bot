from dataclasses import dataclass
from datetime import datetime


@dataclass
class Family:
    id: int
    name: str
    created_at: datetime
    link: str
