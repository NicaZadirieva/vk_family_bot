from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.entities.base import Base


class AuthUsers(Base):
    """
    Таблица для хранения связей для вступления в чат семьи
    """

    __tablename__ = "auth_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    family_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("family.id"), nullable=False
    )
    password_hash = Column(String(255), nullable=False)
