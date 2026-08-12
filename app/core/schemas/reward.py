from dataclasses import dataclass
from datetime import datetime

from pydantic import Field


@dataclass
class Reward:
    id: int
    family_id: int
    name: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    cost: float = Field(0.0, ge=0, description="Стоимость в баллах")
    is_active: bool = True
    deleted_at: datetime | None = None
