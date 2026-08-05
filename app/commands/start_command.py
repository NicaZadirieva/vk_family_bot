from dataclasses import dataclass
from typing import Any
from app.commands.base_command import Command, CommandResult
from app.commands.help_command import HelpCommand
from app.commands.join_command import JoinCommand
from app.domain.family import Family
from app.errors.invalid_login_error import InvalidLoginError
from app.errors.lack_of_data_error import LackOfDataError
from app.services.family_service import FamilyService
from app.services.login_service import LoginService
from app.services.password_service import PasswordService

@dataclass
class LoginContext:
    link: str
    vk_id: int
    user_id: int | None = None


class StartCommand(Command):
    # TODO: возможно придется отрефакторить под паттерн строитель/фабрика
    def __init__(self, login_service: LoginService, password_service: PasswordService, family_service: FamilyService):
        super().__init__()
        self._login_service = login_service
        self._password_service = password_service
        self._family_service = family_service

    def __get_help_command__(self):
        return HelpCommand().for_command("start").with_description("Старт бота").with_usage("start")

    def __get_data_from_context__(self, context: dict[str, Any]) -> LoginContext:
        vk_id = context.get("vk_id")
        link = context.get("link")
        if not vk_id or not link:
            raise LackOfDataError("vk_id, link", {"vk_id": vk_id, "link": link})
        try:
            return LoginContext(vk_id=int(vk_id), link=link)
        except:
            raise InvalidLoginError("vk_id, link не являются валидными", {"vk_id": vk_id, "link": link})
    
    async def execute(self, context: dict[str, Any]):
        # Поиск user_id в БД и текущей семье
        # Если True, в команде Start не делаем ничего
        # Если False, пишет "Вы не состоите в семье. Пожалуйста, войдите через секретный пароль"
        # показывает кнопку "Войти по паролю" (команда /join)
        # 

        try:
            data: LoginContext = self.__get_data_from_context__(context) 
            family: Family | None = await self._family_service.search_family_by_link(data.link)
            if not family:
                """Первый родитель"""
            else:
                is_user_allowed = await self._login_service.is_user_allowed(
                    data.vk_id, family_id=family.id
                )
        except InvalidLoginError as e:
            # TODO: вывести сообщение e.message
            return CommandResult(success=False, error=e.message, next_command=self.__get_help_command__())
        except LackOfDataError as e:
            # TODO: вывести сообщение e.message
            return CommandResult(success=False, error=e.message, next_command=self.__get_help_command__())

        if is_user_allowed:
            return CommandResult(success=True, next_command= )
        else:
            # Вы не состоите в семье. Пожалуйста, войдите через секретный пароль
            return CommandResult(success=False, next_command=JoinCommand(self._password_service))
        
        
