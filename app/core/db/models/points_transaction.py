from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.core.db.models.base import Base
from app.core.db.models.transaction_type import TransactionType


class PointsTransaction(Base):
    __tablename__ = "points_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    child_profile_id = Column(
        Integer, ForeignKey("child_profiles.id"), nullable=False, index=True
    )
    amount = Column(Integer, nullable=False)  # Может быть отрицательным
    transaction_type = Column(Enum(TransactionType), nullable=False)
    reason = Column(Text, nullable=True)
    related_id = Column(
        Integer, nullable=True
    )  # ID связанной сущности (task_id, reward_id и т.д.)
    related_type = Column(
        String(50), nullable=True
    )  # Тип связанной сущности: 'task', 'reward', etc.
    created_by = Column(ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    deleted_at = Column(DateTime, nullable=True)
