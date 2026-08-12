from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.models.base import Base
from app.core.db.models.role import Role


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vk_id: Mapped[str] = mapped_column(String(100), nullable=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("family.id"), nullable=True)
    child_profile_id: Mapped[int] = mapped_column(
        ForeignKey("child_profile.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Москва +3")
    role: Mapped[Role] = mapped_column(Enum(Role, name="role_enum"), nullable=True)
