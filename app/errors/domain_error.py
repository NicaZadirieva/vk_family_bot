from dataclasses import dataclass
from typing import Any


@dataclass
class DomainError(Exception):
    """Базовый класс для доменных ошибок."""

    message: str
    details: dict[str, Any] | None = None

    def __str__(self) -> str:
        return self.message
