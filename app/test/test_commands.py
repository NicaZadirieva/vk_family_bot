import pytest

from app.commands.server_error_command import ServerErrorCommand
from app.handlers.session_storage import SessionStorage


@pytest.fixture
def mock_session():
    return SessionStorage(vk_id=1234, use_redis=False)


@pytest.mark.asyncio
async def test_server_error_cmd(mock_session):
    server_error_cmd = ServerErrorCommand(mock_session)
    cmd_result = await server_error_cmd.execute()
    assert cmd_result.success is True
