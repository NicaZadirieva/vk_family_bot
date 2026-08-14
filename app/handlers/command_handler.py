import json
import logging
from typing import Any

from app.commands.base import ICommand
from app.commands.help import HelpCmd
from app.handlers.command_registry import CommandRegistry
from app.presenter import Presenter

logger = logging.getLogger(__name__)


class CmdHandler:
    def __init__(self, presenter: Presenter):
        self._presenter = presenter

    async def _handle_update(self, update: dict[str, Any]) -> ICommand | None:
        logger.debug(update)

        update_type = update.get("type")
        obj = update.get("object")
        if not obj:
            return None

        message = obj.get("message")
        if not message:
            return None

        vk_id = message.get("from_id")
        if not vk_id:
            return None

        if update_type == "message_new":
            command_name = message.get("text", "")
            if command_name:
                return self._handle_command_name(command_name)
            return HelpCmd(self._presenter)

        elif update_type == "message_event":
            payload = obj.get("payload", {})

            # Преобразуем payload из строки в словарь, если необходимо
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    payload = {}

            command_name = payload.get("command")
            if command_name:
                return self._handle_command_name(command_name)

            return HelpCmd(self._presenter)

        return None

    def _handle_command_name(self, command_name: str) -> ICommand | None:
        """
        Обрабатывает имя команды и возвращает экземпляр команды.
        """
        command_class = CommandRegistry.get_handler(command_name)
        if not command_class:
            return HelpCmd(self._presenter)

        # TODO: ввести проверку перед StartCmd

        # Создаём экземпляр, если это класс
        try:
            return command_class(self._presenter)  # type: ignore
        except TypeError:
            # Если не получается создать экземпляр, возвращаем как есть
            return command_class
