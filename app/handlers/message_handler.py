import json
import logging
from typing import Any

from app.commands.start.start import StartCommand
from app.core.di.services_container import ServicesContainer
from app.core.repositories.base_user_state_repo import UserState
from app.keyboards.keyboard_factory import KeyboardFactory
from app.shared.message_templates import MessageTemplates
from app.vk_api.vk_client import VKClient

logger = logging.getLogger(__name__)


class MessageHandler:
    def __init__(self, vk_client: VKClient, services: ServicesContainer):
        self.vk_client = vk_client
        self.services = services
        self.user_state_service = services.user_state_service()
        self.commands: dict[str, Any] = {}
        self.payload_handlers: dict[str, Any] = {}
        logger.info("🔧 Инициализация MessageHandler...")

        self._register_commands()
        self._register_payload_handlers()

        # Добавьте это логирование
        logger.info(f"✅ Зарегистрированные команды: {list(self.commands.keys())}")
        logger.info(
            f"✅ Зарегистрированные payload handlers: {list(self.payload_handlers.keys())}"
        )

    def _register_commands(self):
        logger.info("📝 Регистрация команд...")

        commands = [
            StartCommand(),
        ]

        for cmd in commands:
            logger.info(f"🔹 Регистрация команды: {cmd.name}")
            self.commands[cmd.name] = cmd
            if hasattr(cmd, "aliases"):
                for alias in cmd.aliases:
                    self.commands[alias] = cmd

        logger.info(f"✅ Команды зарегистрированы: {list(self.commands.keys())}")

    def _register_payload_handlers(self):
        payload_map = {
            "start": "start",
        }

        for payload_action, command_name in payload_map.items():
            if command_name in self.commands:
                self.payload_handlers[payload_action] = self.commands[command_name]

    async def handle_message(
        self, user_id: int, message_text: str, payload: str | None = None
    ):
        try:
            state = await self.user_state_service.get_or_create_user_state(
                user_id, default_state=UserState(user_id)
            )
            logger.debug(f"🔍 Текущий screen пользователя: {state.current_screen}")
            response, screen_type = await self._process_message(
                user_id, message_text, payload, state
            )

            await self._send_response(user_id, response, screen_type)

        except Exception as e:
            await self._handle_error(user_id, e)

    async def _process_message(
        self, user_id: int, message_text: str, payload: str | None, state: UserState
    ) -> tuple[str, str]:
        # Удаляем невидимые символы
        clean_text = message_text.strip() if message_text else ""

        # 1. Обработка payload (приоритет 1)
        if payload:
            result = await self._handle_payload(user_id, payload, state)
            if result:
                return result

        # 3. Обработка текстовых команд (приоритет 2)
        command_key = clean_text.lower()
        if command_key in self.commands:
            logger.info(f"✅ Выполняем команду: {command_key}")
            return await self.commands[command_key].execute(user_id, state)

        # 2. Обработка состояния (приоритет 3)
        from app.states import get_state

        state_handler = get_state(state.current_screen, self.services)
        if state_handler:
            return await state_handler.handle(user_id, clean_text, state)

        # 4. Обработка команд с / (приоритет 4)
        if clean_text.startswith("/"):
            command_name = clean_text[1:].lower()
            logger.info(f"🔍 command_name: '{command_name}'")
            if command_name in self.commands:
                return await self.commands[command_name].execute(user_id, state)
        logger.warning(
            f"❌ Команда не найдена. clean_text: '{clean_text}', command_key: '{command_key}'"
        )
        return MessageTemplates.UNKNOWN_COMMAND, "main"

    def __clear_payload_data__(self, payload_data: dict):
        available_keys = ["month", "month_name", "person_id", "person_name"]
        cleared_data = {}
        for key in available_keys:
            if key in payload_data:
                cleared_data[key] = payload_data[key]
        return cleared_data

    async def _handle_payload(
        self, user_id: int, payload: str, state: UserState
    ) -> tuple[str, str] | None:
        try:
            payload_data = json.loads(payload) if isinstance(payload, str) else payload
            action = payload_data.get("action")

            if action in self.payload_handlers:
                command = self.payload_handlers[action]
                state.data.update(self.__clear_payload_data__(payload_data))
                return await command.execute(user_id, state, payload_data)

        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Ошибка парсинга payload: {e}")

        return None

    # TODO: нарушение SOLID
    async def _send_response(self, user_id: int, text: str, screen_type: str) -> None:
        keyboard = KeyboardFactory.create(screen_type)
        await self.vk_client.send_message(user_id, text, keyboard=keyboard)

    async def _handle_error(self, user_id: int, error: Exception) -> None:
        logger.error(
            f"❌ Ошибка при обработке сообщения от {user_id}: {error}", exc_info=True
        )
        await self._send_response(
            user_id,
            MessageTemplates.SYSTEM_ERROR,
            "main",
        )
