from dataclasses import dataclass
from typing import Any

from app.commands.base.base_command import Command
from app.commands.create_family.create_family_cmd import CreateFamilyCmd
from app.commands.help.help_command import HelpCommand
from app.commands.join.join_command import JoinCommand
from app.commands.server_error_command import ServerErrorCommand
from app.commands.start.start_cmd import StartCommand
from app.handlers.session_storage import SessionStorage
from app.services.family_service import FamilyService
from app.services.login_service import LoginService
from app.services.password_service import PasswordService


@dataclass
class CommandDependencies:
    """Контейнер для зависимостей команд"""

    session: SessionStorage
    password_service: PasswordService
    login_service: LoginService
    family_service: FamilyService


class CommandFactory:
    """Фабрика для создания команд"""

    def __init__(self, dependencies: CommandDependencies):
        self._deps = dependencies
        self._commands: dict[str, Any] = {}

    def create_start_command(self) -> StartCommand:
        return StartCommand(
            login_service=self._deps.login_service,
            password_service=self._deps.password_service,
            family_service=self._deps.family_service,
            session=self._deps.session,
            command_factory=self,
        )

    def create_create_family_command(self) -> CreateFamilyCmd:
        return CreateFamilyCmd(
            login_service=self._deps.login_service,
            password_service=self._deps.password_service,
            family_service=self._deps.family_service,
            session=self._deps.session,
        )

    def create_join_command(self) -> JoinCommand:
        return JoinCommand(password_service=self._deps.password_service)

    def create_help_command(self) -> HelpCommand:
        return HelpCommand()

    def create_server_error_command(self) -> ServerErrorCommand:
        return ServerErrorCommand()

    def get_command(self, command_name: str) -> Command:
        """Ленивое создание команд"""
        if command_name not in self._commands:
            creators = {
                "start": self.create_start_command,
                "create_family": self.create_create_family_command,
                "join": self.create_join_command,
                "help": self.create_help_command,
                "error": self.create_server_error_command,
            }
            if command_name in creators:
                self._commands[command_name] = creators[command_name]()
            else:
                raise ValueError(f"Неизвестная команда: {command_name}")

        return self._commands[command_name]
