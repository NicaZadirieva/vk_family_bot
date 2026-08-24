from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.db.models.base import Base
from app.core.db.models.permission import Permission


class Invite(Base):
    __tablename__ = "invites"

    id = Column(Integer, primary_key=True)
    code = Column(String(32), unique=True, nullable=False)
    created_by_id = Column(Integer, ForeignKey("user.id"))
    role = Column(Enum(Permission), default=Permission.USER)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    used_by_id = Column(Integer, ForeignKey("user.id"), nullable=True)

    creator = relationship("User", foreign_keys=[created_by_id])
    used_by = relationship("User", foreign_keys=[used_by_id])
