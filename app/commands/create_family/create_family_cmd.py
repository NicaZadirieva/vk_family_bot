from typing import Any

from app.commands.base.base_command import Command, CommandResult
from app.commands.create_family.create_family_scene import CreateFamilyScene
from app.handlers.session_storage import SessionStorage
from app.services.family_service import FamilyService
from app.services.auth_service import LoginService
from app.services.password_service import PasswordService


class CreateFamilyCmd(Command):
    """Команда создания семьи"""

    def __init__(
        self,
        login_service: LoginService,
        password_service: PasswordService,
        family_service: FamilyService,
        session: SessionStorage,
    ):
        super().__init__()
        self._login_service = login_service
        self._password_service = password_service
        self._family_service = family_service
        self.scene = CreateFamilyScene(
            login_service, password_service, family_service, session
        )
        self._next_command = None

    async def execute(self, context: dict[str, Any]) -> CommandResult:
        """Выполняет команду создания семьи"""
        try:
            vk_id = context.get("vk_id")
            text = context.get("text", "")

            if not vk_id:
                return CommandResult(
                    success=False, error="user_id не указан в контексте"
                )

            # Проверяем, есть ли активная сцена
            if self.scene.is_active(vk_id):
                # Продолжаем сцену
                is_completed, response = await self.scene.process_message(vk_id, text)

                # Отправляем ответ пользователю
                await self._send_message(vk_id, response)

                if is_completed:
                    # Сцена завершена
                    self.scene.end(vk_id)

                    # Если есть следующая команда в цепочке
                    if self._next_command:
                        return CommandResult(
                            success=True,
                            data={"family_created": True},
                            next_command=self._next_command,
                        )

                    return CommandResult(success=True, data={"family_created": True})
                else:
                    # Сцена продолжается
                    return CommandResult(success=True, data={"scene_active": True})

            # Запускаем новую сцену
            if text == "/create_family":
                greeting = await self.scene.start(vk_id)
                await self._send_message(vk_id, greeting.message)
                return CommandResult(success=True, data={"scene_started": True})

            return CommandResult(
                success=False,
                error="Используйте команду /create_family для создания семьи",
            )

        except Exception as e:
            return CommandResult(
                success=False, error=f"Ошибка при создании семьи: {str(e)}"
            )

    def _get_next(self, result: CommandResult[dict[str, Any]]) -> Command | None:
        """Получить следующую команду в цепочке"""
        if result.success and result.data and result.data.get("family_created"):
            return self._next_command
        return None

    async def _send_message(self, vk_id: int, text: str):
        """Отправка сообщения (заглушка)"""
        # Здесь должна быть реальная отправка сообщения
        print(f"Сообщение для {vk_id}: {text}")
        # await vk_api.messages.send(user_id=user_id, message=text)
