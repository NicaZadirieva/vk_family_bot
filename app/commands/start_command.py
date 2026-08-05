from dataclasses import dataclass
from typing import Any
from app.commands.base_command import Command, CommandResult
from app.errors.invalid_login_error import InvalidLoginError
from app.errors.lack_of_data_error import LackOfDataError
from app.services.login_service import LoginService

@dataclass
class LoginContext:
    family_id: int
    vk_id: int
    user_id: int | None = None


class StartCommand(Command):
    # TODO: возможно придется отрефакторить под паттерн строитель/фабрика
    def __init__(self, login_service: LoginService):
        super().__init__()
        self._login_service = login_service

    def __get_data_from_context__(self, context: dict[str, Any]) -> LoginContext:
        vk_id = context.get("vk_id")
        family_id = context.get("family_id")
        if not vk_id or not family_id:
            raise LackOfDataError("vk_id, family_id", {"vk_id": vk_id, "family_id": family_id})
        try:
            return LoginContext(vk_id=int(vk_id), family_id=int(family_id))
        except:
            raise InvalidLoginError("vk_id, family_id не являются валидными id", {"vk_id": vk_id, "family_id": family_id})
    
    async def execute(self, context: dict[str, Any]):
        # Поиск user_id в БД и текущей семье
        # Если True, в команде Start не делаем ничего
        # Если False, пишет "Вы не состоите в семье. Пожалуйста, войдите через секретный пароль"
        # показывает кнопку "Войти по паролю" (команда /join)
        try:
            data: LoginContext = self.__get_data_from_context__(context) 
            is_user_allowed = await self._login_service.is_user_allowed(
            data.vk_id, data.family_id
        )
        except InvalidLoginError as e:
            return CommandResult(success=False, error=e.message, next_command=)
        except LackOfDataError as e:
            return CommandResult(success=False, error=e.message, next_command=)

        if is_user_allowed:
            return CommandResult(success=True, next_command=)
        else:
            # непредвиденная ситуация
            return CommandResult(success=False, next_command=)
        
        
