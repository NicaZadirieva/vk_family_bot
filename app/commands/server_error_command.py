from typing import Any

from app.commands.base_command import Command, CommandResult


class ServerErrorCommand(Command):
    async def execute(self, context: dict[str, Any]):
        # TODO: сделать кнопку пни разработчика
        # TODO: вывести сообщение "Произошла ошибка со стороны сервера. Обратитесь по адресу no.demchenko@yandex.ru, чтобы пнуть разработчика"
        return CommandResult(success=True)
