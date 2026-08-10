import logging
from dataclasses import dataclass
from typing import Any

from app.commands.base.base_command import Command, CommandResult
from app.commands.dependencies import CommandFactory
from app.commands.help.help_command import HelpCommand
from app.commands.start.start_scene import StartScene
from app.errors.invalid_login_error import InvalidLoginError
from app.errors.lack_of_data_error import LackOfDataError
from app.handlers.session_storage import SessionStorage
from app.services.family_service import FamilyService
from app.services.login_service import LoginService
from app.services.password_service import PasswordService

logger = logging.getLogger(__name__)


@dataclass
class LoginContext:
    link: str
    vk_id: int
    user_id: int | None = None


class StartCommand(Command):
    def __init__(
        self,
        login_service: LoginService,
        password_service: PasswordService,
        family_service: FamilyService,
        session: SessionStorage,
        command_factory: CommandFactory,
    ):
        super().__init__()
        self._login_service = login_service
        self._password_service = password_service
        self._family_service = family_service
        self.scene = StartScene(
            family_service=family_service,
            login_service=login_service,
            password_service=password_service,
            session=session,
            command_factory=command_factory,
        )
        self._next_command = None

    def __get_help_command__(self):
        return (
            HelpCommand()
            .for_command("start")
            .with_description("Старт бота")
            .with_usage("start")
        )

    def __get_data_from_context__(self, context: dict[str, Any]) -> LoginContext:
        vk_id = context.get("vk_id")
        link = context.get("link")
        if not vk_id or not link:
            raise LackOfDataError("vk_id, link", {"vk_id": vk_id, "link": link})
        try:
            return LoginContext(vk_id=int(vk_id), link=link)
        except:
            raise InvalidLoginError(
                "vk_id, link не являются валидными", {"vk_id": vk_id, "link": link}
            )

    async def execute(self, context: dict[str, Any]):
        # Поиск user_id в БД и текущей семье
        # Если True, в команде Start не делаем ничего
        # Если False, пишет "Вы не состоите в семье. Пожалуйста, войдите через секретный пароль"
        # показывает кнопку "Войти по паролю" (команда /join)
        #

        try:
            data: LoginContext = self.__get_data_from_context__(context)
            # Проверяем, есть ли активная сцена
            text = context.get("text", "")
            if self.scene.is_active(data.vk_id):
                # Продолжаем сцену
                is_completed, response = await self.scene.process_message(
                    data.vk_id, text
                )

                # Отправляем ответ пользователю
                await self._send_message(data.vk_id, response)

                if is_completed:
                    # Сцена завершена
                    self.scene.end(data.vk_id)

                    # Если есть следующая команда в цепочке
                    if self._next_command:
                        return CommandResult(
                            success=True,
                            data={"start": True},
                            next_command=self._next_command,
                        )

                    return CommandResult(success=True, data={"start": True})
                else:
                    # Сцена продолжается
                    return CommandResult(success=True, data={"scene_active": True})

            # Запускаем новую сцену
            if text == "/start":
                greeting = await self.scene.start(data.vk_id)
                await self._send_message(data.vk_id, greeting.message)
                return CommandResult(success=True, data={"scene_started": True})

            return CommandResult(
                success=False,
                error="Используйте команду /start для входа в бота",
            )
        except InvalidLoginError as e:
            # TODO: вывести сообщение e.message для пользователя VK
            logger.error(e)
            return CommandResult(
                success=False, error=e.message, next_command=self.__get_help_command__()
            )
        except LackOfDataError as e:
            # TODO: вывести сообщение e.message для пользователя VK
            logger.error(e)
            return CommandResult(
                success=False, error=e.message, next_command=self.__get_help_command__()
            )

    async def _send_message(self, vk_id: int, text: str):
        """Отправка сообщения (заглушка)"""
        # Здесь должна быть реальная отправка сообщения
        print(f"Сообщение для {vk_id}: {text}")
        # await vk_api.messages.send(user_id=user_id, message=text)
