from typing import Any

from app.shared.message_templates import MessageTemplates

from .base import IState


class MainState(IState):
    @property
    def name(self) -> str:
        return "main"

    async def enter(
        self, user_id: int, state: Any, payload: dict | None = None
    ) -> tuple[str, str]:
        state.current_screen = "main"
        state.data = {}
        return MessageTemplates.START, "main"

    async def handle(self, user_id: int, text: str, state: Any) -> tuple[str, str]:
        # В главном состоянии обрабатываем только команды
        return MessageTemplates.UNKNOWN_COMMAND, "main"
