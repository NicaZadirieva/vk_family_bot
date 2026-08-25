from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.models.base import Base
from app.core.db.models.permission import Permission
from app.core.db.models.role import Role


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # TODO: перегенерировать эту таблицу из-за unique и nullable=False
    vk_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("family.id"), nullable=True)
    child_profile_id: Mapped[int] = mapped_column(
        ForeignKey("child_profile.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Москва +3")
    role: Mapped[Role] = mapped_column(Enum(Role, name="role_enum"), nullable=True)

    permission: Mapped[Permission] = mapped_column(
        Enum(Permission, name="permission_enum"),
        nullable=False,
        default=Permission.USER,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    invited_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
