from app.core.schemas.role import Role


class User:
    __tablename__ = "user"

    id: int
    vk_id: str
    name: str
    timezone: str = "Москва +3"
    family_id: int | None = None
    child_profile_id: int | None = None
    role: Role | None = None
