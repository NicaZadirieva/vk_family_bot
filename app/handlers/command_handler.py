import json
import logging
from dataclasses import dataclass
from typing import Any

from app.commands.base import ICommand
from app.commands.help import HelpCmd
from app.commands.profile.master.create_family import CreateFamilyCmd
from app.core.schemas.family import Family
from app.core.services.family import FamilyService
from app.exceptions.not_found_error import NotFoundError
from app.handlers.command_registry import CommandRegistry
from app.handlers.user_info import UserInfo
from app.presenter import Presenter

logger = logging.getLogger(__name__)


class CmdHandler:
    def __init__(self, presenter: Presenter, family_service: FamilyService):
        self._presenter = presenter
        self._service = family_service

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

        link = self._get_chat_link(message)

        if update_type == "message_new":
            command_name = message.get("text", "")
            if command_name:
                return await self._handle_command_name(
                    command_name, UserInfo(link=link, vk_id=vk_id, family=None)
                )
            return HelpCmd(self._presenter)

        elif update_type == "message_event":
            payload = obj.get("payload", {})

            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    payload = {}

            command_name = payload.get("command")
            if command_name:
                return await self._handle_command_name(
                    command_name, UserInfo(link=link, vk_id=vk_id, family=None)
                )

            return HelpCmd(self._presenter)

        return None

    def _get_chat_link(self, message: dict[str, Any]) -> str | None:
        """
        Получает ссылку на чат VK из сообщения.
        """
        peer_id = message.get("peer_id")
        if not peer_id:
            return None

        # Если это личное сообщение (peer_id > 0 и < 2000000000)
        if 0 < peer_id < 2000000000:
            return f"https://vk.com/im?sel={peer_id}"

        # Если это беседа (peer_id >= 2000000000)
        elif peer_id >= 2000000000:
            chat_id = peer_id - 2000000000
            return f"https://vk.com/im?sel=c{chat_id}"

        return None

    async def _handle_command_name(
        self, command_name: str, user_info: UserInfo)
        """
        Обрабатывает имя команды и возвращает экземпляр команды.
        """
        command_class = CommandRegistry.get_handler(command_name)

        if not command_class or not user_info.link:
            return HelpCmd(self._presenter)

        try:
            user_info.family = await self._service.get_family_by_link(user_info.link)
            return command_class(self._presenter, user_info, self._service)  # type: ignore
        except TypeError:
            # Если не получается создать экземпляр, возвращаем как есть
            return command_class
        except NotFoundError:
            return CreateFamilyCmd(self._presenter, user_info, family_service=self._service)
