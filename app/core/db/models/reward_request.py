from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.sql import func

from app.core.db.models.base import Base
from app.core.db.models.request_status import RequestStatus


class RewardRequest(Base):
    __tablename__ = "reward_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    child_profile_id = Column(
        Integer, ForeignKey("child_profile.id"), nullable=False, index=True
    )
    reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=False, index=True)
    status = Column(Enum(RequestStatus), nullable=False, default=RequestStatus.PENDING)
    comment = Column(Text, nullable=True)  # Комментарий от ребенка или родителя
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    processed_at = Column(DateTime, nullable=True)  # Когда обработали
    processed_by = Column(ForeignKey("user.id"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)
