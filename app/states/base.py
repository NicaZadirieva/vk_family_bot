from abc import ABC, abstractmethod
from typing import Any


class IState(ABC):
    """Базовый интерфейс состояния."""

    @abstractmethod
    async def handle(self, user_id: int, text: str, state: Any) -> tuple[str, str]:
        """Обрабатывает ввод в данном состоянии."""

    @abstractmethod
    async def enter(
        self, user_id: int, state: Any, payload: dict | None = None
    ) -> tuple[str, str]:
        """Вызывается при входе в состояние."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Название состояния."""
