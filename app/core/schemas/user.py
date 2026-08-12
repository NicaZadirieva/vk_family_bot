from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int
    name: str
    created_at: datetime
