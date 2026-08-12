from enum import Enum


class TransactionType(Enum):
    EARNED = "earned"  # Заработал (за задачу)
    SPENT = "spent"  # Потратил (на награду)
    BONUS = "bonus"  # Бонус (от родителей)
    PENALTY = "penalty"  # Штраф (за нарушение)
    REFUND = "refund"  # Возврат (отмена награды)
    ADJUSTMENT = "adjustment"  # Ручная корректировка
