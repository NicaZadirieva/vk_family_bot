from unittest.mock import AsyncMock

from app.commands.dependencies import CommandDependencies, CommandFactory
from app.commands.start.start_cmd import StartCommand
from app.handlers.session_storage import SessionStorage
from app.services.family_service import FamilyService
from app.services.login_service import LoginService
from app.services.password_service import PasswordService


async def test_start_cmd_success():
    login_service = AsyncMock(spec=LoginService)
    password_service = AsyncMock(spec=PasswordService)
    family_service = AsyncMock(spec=FamilyService)
    session = AsyncMock(spec=SessionStorage)
    command_factory = CommandFactory(
        CommandDependencies(
            login_service=login_service,
            password_service=password_service,
            family_service=family_service,
            session=session,
        )
    )

    start_cmd = StartCommand(
        login_service, password_service, family_service, session, command_factory
    )
    start_cmd._send_message = AsyncMock()
    context = {
        "vk_id": 123,
        "link": "https://vk.ru/im/convo/223232323?entrypoint=list_all",
        "text": "/start",
    }
    res = await start_cmd.execute(context)
    assert res.success is True
