import logging
from typing import Any

from app.commands.base_command import Command, CommandResult
from app.commands.help_command import HelpCommand
from app.commands.server_error_command import ServerErrorCommand
from app.core.join_context import JoinContext
from app.errors.invalid_login_error import InvalidLoginError
from app.errors.lack_of_data_error import LackOfDataError
from app.errors.resource_not_found_error import ResourceNotFoundError
from app.handlers.session_storage import SessionStorage
from app.services.password_service import PasswordService

logger = logging.getLogger(__name__)


class JoinCommand(Command):
    """
    Вход с паролем
    """

    def __init__(self, session: SessionStorage, password_service: PasswordService):
        super().__init__(session)
        self._password_service = password_service

    def __get_help_command__(self):
        return (
            HelpCommand(self.session)
            .for_command("join")
            .with_description("Вход по паролю в чат семьи")
            .with_usage("/join <пароль>")
            .then(JoinCommand(self.session, self._password_service))
        )

    def __get_data_from_context__(self, password: str) -> JoinContext:
        vk_id = self.session.get("vk_id")
        family_id = self.session.get("family_id")
        user_id = self.session.get("user_id")
        if not vk_id or not family_id or not user_id or not password:
            raise LackOfDataError(
                "vk_id, family_id, user_id",
                {"vk_id": vk_id, "family_id": family_id, "user_id": user_id},
            )
        try:
            return JoinContext(
                password=password,
                vk_id=int(vk_id),
                family_id=int(family_id),
                user_id=int(user_id),
            )
        except:  # noqa: E722
            raise InvalidLoginError(
                "vk_id, family_id не являются валидными id",
                {"vk_id": vk_id, "family_id": family_id},
            )

    async def execute(self):
        try:
            data: JoinContext = self.__get_data_from_context__(
                self.session.get("password")
            )
            is_verified_user = await self._password_service.verify_user(data)
            if is_verified_user:
                # TODO: написать команду по показу сообщения об успешном входе в чат семьи
                return CommandResult(success=True)  # , next_command=)
            else:
                # TODO: вернуть пользователя к вводу пароля
                return CommandResult(
                    success=False,
                    next_command=JoinCommand(self.session, self._password_service),
                )
        except ResourceNotFoundError as e:
            logger.error(f"Resource not found: {e.message}", exc_info=True)
            return CommandResult(
                success=False, error=e.message, next_command=self.__get_help_command__()
            )
        except LackOfDataError as e:
            logger.error(f"Missing required data: {e.message}", exc_info=True)
            return CommandResult(
                success=False, error=e.message, next_command=self.__get_help_command__()
            )
        except InvalidLoginError as e:
            logger.error(f"Authentication failed: {e.message}", exc_info=True)
            return CommandResult(
                success=False, error=e.message, next_command=self.__get_help_command__()
            )
        except Exception as e:
            logger.exception(f"Unexpected error in {self.__class__.__name__}: {e}")
            return CommandResult(
                success=False, next_command=ServerErrorCommand(self.session)
            )
