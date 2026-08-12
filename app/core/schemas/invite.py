from dataclasses import dataclass
from datetime import datetime

from app.core.schemas.permission import Permission


@dataclass
class Invite:
    id: int
    code: str
    created_by_id: int
    expires_at: datetime
    used_by_id: int
    role: Permission = Permission.USER
    used: bool = False
