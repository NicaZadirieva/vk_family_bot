# Команда ServerError
import pytest

from app.commands.server_error_command import ServerErrorCommand


@pytest.mark.asyncio
async def test_server_error_cmd():
    server_error_cmd = ServerErrorCommand()
    cmd_result = await server_error_cmd.execute({})
    assert cmd_result.success is True
