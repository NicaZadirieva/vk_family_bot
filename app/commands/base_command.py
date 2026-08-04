from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, TypeVar

T = TypeVar("T")


@dataclass
class CommandResult[T]:
    """Результат выполнения команды."""

    success: bool
    data: T | None = None
    error: str | None = None
    next_command: Optional["Command"] = None  # Следующая команда


class Command[T](ABC):
    """Абстрактная команда."""

    def __init__(self):
        self._next_on_success: Command | None = None
        self._next_on_failure: Command | None = None

    @abstractmethod
    def execute(self, context: dict[str, Any]) -> CommandResult[T]:
        """Выполняет команду.

        Args:
            context: Контекст выполнения (данные между командами)

        Returns:
            CommandResult: Результат выполнения
        """

    def then(self, command: "Command") -> "Command":
        """Устанавливает команду для выполнения при успехе (fluent interface)."""
        self._next_on_success = command
        return self

    def otherwise(self, command: "Command") -> "Command":
        """Устанавливает команду для выполнения при ошибке (fluent interface)."""
        self._next_on_failure = command
        return self

    def _get_next(self, result: CommandResult) -> Optional["Command"]:
        """Возвращает следующую команду в зависимости от результата."""
        return self._next_on_success if result.success else self._next_on_failure
