from dataclasses import dataclass
from datetime import datetime

from app.core.schemas.transaction_type import TransactionType


@dataclass
class PointsTransaction:
    """Модель транзакции баллов"""

    id: int
    child_profile_id: int
    amount: int  # Может быть отрицательным
    created_by: int
    created_at: datetime
    transaction_type: TransactionType
    reason: str | None = None
    related_id: int | None = None  # ID связанной сущности
    related_type: str | None = None  # Тип связанной сущности: 'task', 'reward', etc.
    deleted_at: datetime | None = None

    def __post_init__(self):
        """Валидация после инициализации"""
        if self.id < 0:
            raise ValueError("id не может быть отрицательным")
        if self.child_profile_id < 0:
            raise ValueError("child_profile_id не может быть отрицательным")
        if self.amount == 0:
            raise ValueError("amount не может быть равен 0")
        if self.created_by < 0:
            raise ValueError("created_by не может быть отрицательным")

        # Валидация связанной сущности
        if self.related_id is not None and self.related_type is None:
            raise ValueError("related_type обязателен, если указан related_id")
        if self.related_type is not None and self.related_id is None:
            raise ValueError("related_id обязателен, если указан related_type")

        # Валидация типа связанной сущности
        if self.related_type is not None:
            allowed_types = ["task", "reward", "adjustment", "bonus", "penalty"]
            if self.related_type not in allowed_types:
                raise ValueError(f"related_type должен быть одним из: {allowed_types}")

        # Валидация суммы в зависимости от типа транзакции
        if self.transaction_type in [TransactionType.SPENT, TransactionType.PENALTY]:
            if self.amount > 0:
                raise ValueError(
                    f"При типе {self.transaction_type} amount должен быть отрицательным"
                )
        elif (
            self.transaction_type in [TransactionType.EARNED, TransactionType.BONUS]
            and self.amount < 0
        ):
            raise ValueError(
                f"При типе {self.transaction_type} amount должен быть положительным"
            )
