from abc import ABC, abstractmethod

from app.core.repositories.base_user_state_repo import UserState


class ICommand(ABC):
    """Базовый класс для всех команд."""

    @abstractmethod
    async def execute(
        self, user_id: int, state: UserState, payload: dict | None = None
    ) -> tuple[str, str]:
        """Выполняет команду и возвращает (текст_ответа, экран)."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Название команды для регистрации."""
