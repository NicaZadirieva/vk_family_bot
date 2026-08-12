from dataclasses import dataclass
from datetime import datetime

from app.core.schemas.permission import Permission
from app.core.schemas.role import Role


@dataclass
class User:
    id: int
    vk_id: str
    name: str
    created_at: datetime
    invited_by_id: int
    password_hash: str
    timezone: str = "Москва +3"
    family_id: int | None = None
    child_profile_id: int | None = None
    role: Role | None = None
    permission: Permission = Permission.USER
    is_active: bool = True
