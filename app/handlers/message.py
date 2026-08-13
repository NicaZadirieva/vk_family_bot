import logging

from app.keyboards.keyboard_factory import KeyboardFactory
from app.vk_api.vk_client import VKClient

logger = logging.getLogger(__name__)


class MessageHandler:
    def __init__(self, vk_client: VKClient):  # , service: PersonService)
        self.vk_client = vk_client
        # self.service = service

        # Регистрация всех команд
        self._register_commands()

    def _register_commands(self):
        """Регистрация команд с алиасами."""

        # Команда старта
        # CommandRegistry.register(
        #    handler=self._handle_start,
        #    name="start",
        #    aliases=["старт", "привет", "начать"],
        # )

    async def _send_response(self, user_id: int, text: str, screen_type: str) -> None:
        """Отправка ответа с клавиатурой."""
        keyboard = KeyboardFactory.create(screen_type)
        await self.vk_client.send_message(user_id, text, keyboard=keyboard)
