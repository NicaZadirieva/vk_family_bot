from app.keyboards.keyboard_factory import KeyboardFactory
from app.vk_api.vk_client import VKClient


class Presenter:
    """Отвечает за отправку сообщений и клавиатур."""

    def __init__(self, vk_client: VKClient):
        self.vk_client = vk_client

    async def show(self, vk_id: int, text: str, screen_type: str, **kwargs) -> None:
        """Показать сообщение с клавиатурой."""
        keyboard = KeyboardFactory.create(screen_type, **kwargs)
        await self.vk_client.send_message(vk_id, text, keyboard=keyboard)

    async def show_only_text(self, vk_id: int, text: str) -> None:
        """Показать сообщение"""
        await self.vk_client.send_message(vk_id, text)

    async def show_error(self, vk_id: int, error_text: str) -> None:
        """Показать сообщение об ошибке."""
        await self.show(vk_id, f"❌ {error_text}", "main")

    async def show_success(self, vk_id: int, success_text: str) -> None:
        """Показать сообщение об успехе."""
        await self.show(vk_id, f"✅ {success_text}", "main")
