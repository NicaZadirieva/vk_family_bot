from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import time
from enum import Enum, auto
from typing import Any

from app.commands.base.base_command import Command


class SceneState(Enum):
    """Состояния сцены"""

    WAITING_INPUT = auto()  # Ожидает ввод пользователя
    PROCESSING = auto()  # Обрабатывает данные
    COMPLETED = auto()  # Завершена
    CANCELLED = auto()  # Отменена


@dataclass
class SceneContext:
    """Контекст выполнения сцены"""

    scene_id: str
    user_id: int
    step: Any = 0
    state: SceneState = SceneState.WAITING_INPUT
    data: dict[str, Any] = field(default_factory=dict)
    temp_data: dict[str, Any] = field(default_factory=dict)  # Для временных данных


class Scene(ABC):
    """Базовый класс для всех сцен"""

    def __init__(self, scene_id: str):
        self.scene_id = scene_id
        self.timeout = 300  # Таймаут в секундах (5 минут)
        self._active_sessions: dict[int, SceneContext] = {}

    @abstractmethod
    async def on_enter(self, user_id: int, context: SceneContext) -> str:
        """Вызывается при входе в сцену. Возвращает приветственное сообщение"""
        raise NotImplementedError("Метод on_enter должен быть реализован")

    @abstractmethod
    async def on_message(
        self, user_id: int, text: str, context: SceneContext
    ) -> tuple[bool, str]:
        """
        Обрабатывает сообщение пользователя
        Возвращает (завершена_ли_сцена, сообщение_для_отправки)
        """
        raise NotImplementedError("Метод on_message должен быть реализован")

    @abstractmethod
    async def on_exit(self, user_id: int, context: SceneContext) -> str:
        """Вызывается при выходе из сцены. Возвращает прощальное сообщение"""
        return "Сцена завершена. Спасибо!"

    def is_active(self, user_id: int) -> bool:
        """Проверяет, активна ли сцена для пользователя"""
        return user_id in self._active_sessions

    def get_context(self, user_id: int) -> SceneContext | None:
        """Получает контекст сцены"""
        return self._active_sessions.get(user_id)

    async def start(self, user_id: int) -> str:
        """Начинает сцену"""
        context = SceneContext(user_id=user_id, scene_id=self.scene_id)
        self._active_sessions[user_id] = context
        return await self.on_enter(user_id, context)

    def end(self, user_id: int):
        """Завершает сцену без вызова on_exit"""
        if user_id in self._active_sessions:
            del self._active_sessions[user_id]

    async def finish(self, user_id: int) -> str:
        """Завершает сцену с вызовом on_exit"""
        context = self.get_context(user_id)
        if not context:
            return "Сцена не найдена."

        exit_message = await self.on_exit(user_id, context)
        self.end(user_id)
        return exit_message

    async def process_message(self, user_id: int, text: str) -> tuple[bool, str]:
        """Обрабатывает сообщение"""
        context = self.get_context(user_id)
        if not context:
            return False, "У вас нет активной сцены"

        is_completed, response = await self.on_message(user_id, text, context)

        if is_completed:
            exit_message = await self.finish(user_id)
            return True, f"{response}\n\n{exit_message}"

        return False, response
