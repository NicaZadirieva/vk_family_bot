from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.models.base import Base


class Family(Base):
    __tablename__ = "family"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    # TODO: перестроить базу под это поле
    created_by: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    link: Mapped[str] = mapped_column(String(50), nullable=False)
