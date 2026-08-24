from dataclasses import dataclass

from app.core.schemas.family import Family


@dataclass
class UserInfo:
    vk_id: str | None
    family: Family | None
    link: str | None
