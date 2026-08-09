from unittest.mock import AsyncMock, patch

import pytest

from app.commands.help_command import HelpCommand
from app.commands.join_command import JoinCommand
from app.commands.server_error_command import ServerErrorCommand
from app.errors.invalid_login_error import InvalidLoginError
from app.errors.lack_of_data_error import LackOfDataError
from app.errors.resource_not_found_error import ResourceNotFoundError
from app.services.password_service import PasswordService


# Команда ServerError
@pytest.mark.asyncio
async def test_server_error_cmd():
    server_error_cmd = ServerErrorCommand()
    cmd_result = await server_error_cmd.execute({})
    assert cmd_result.success is True


# Команда Join


@pytest.mark.asyncio
async def test_join_cmd_success():
    password_service = AsyncMock(spec=PasswordService)
    password_service.verify_user.return_value = True
    join_cmd = JoinCommand(
        password_service=password_service,
    )

    res = await join_cmd.execute(
        {"password": 123, "vk_id": 1234, "family_id": 5678, "user_id": 123}
    )

    assert res.success is True

    # TODO: дописать next_command


@pytest.mark.asyncio
async def test_join_cmd_user_not_verified():
    password_service = AsyncMock(spec=PasswordService)
    password_service.verify_user.return_value = False
    join_cmd = JoinCommand(
        password_service=password_service,
    )

    res = await join_cmd.execute(
        {"password": 123, "vk_id": 1234, "family_id": 5678, "user_id": 123}
    )
    # TODO: вернуть пользователя к вводу пароля
    assert res.success is False
    assert isinstance(res.next_command, JoinCommand)


@pytest.mark.asyncio
async def test_join_cmd_user_not_found():
    password_service = AsyncMock(spec=PasswordService)
    password_service.verify_user.side_effect = ResourceNotFoundError
    join_cmd = JoinCommand(
        password_service=password_service,
    )

    res = await join_cmd.execute({"vk_id": 1234, "family_id": 5678, "user_id": 123})
    assert res.success is False
    assert isinstance(res.next_command, HelpCommand)


@pytest.mark.asyncio
async def test_join_cmd_no_required_info():
    password_service = AsyncMock(spec=PasswordService)
    join_cmd = JoinCommand(
        password_service=password_service,
    )

    # Используем patch для замены метода
    with patch.object(
        join_cmd,
        "get_data_from_context",
        side_effect=LackOfDataError(
            "vk_id, family_id, user_id",
            {"vk_id": None, "family_id": 5678, "user_id": 1234},
        ),
    ):
        res = await join_cmd.execute({"vk_id": None, "family_id": 5678, "user_id": 123})
    assert res.success is False
    assert isinstance(res.next_command, HelpCommand)


@pytest.mark.asyncio
async def test_join_cmd_auth_failed():
    password_service = AsyncMock(spec=PasswordService)
    join_cmd = AsyncMock(spec=JoinCommand)
    join_cmd.password_service = password_service
    join_cmd = JoinCommand(
        password_service=password_service,
    )

    # Используем patch для замены метода
    with patch.object(
        join_cmd,
        "get_data_from_context",
        side_effect=InvalidLoginError(
            "vk_id, family_id, user_id",
            {"vk_id": 1234, "family_id": "some invalid data", "user_id": 1234},
        ),
    ):
        res = await join_cmd.execute({"vk_id": 1234, "family_id": 5678, "user_id": 123})
    assert res.success is False
    assert isinstance(res.next_command, HelpCommand)


@pytest.mark.asyncio
async def test_join_cmd_unexpected_error():
    password_service = AsyncMock(spec=PasswordService)
    join_cmd = AsyncMock(spec=JoinCommand)
    join_cmd.password_service = password_service
    join_cmd = JoinCommand(
        password_service=password_service,
    )
    # Здесь умышленно бросается исключение независимо от context
    with patch.object(
        join_cmd,
        "get_data_from_context",
        side_effect=Exception(),
    ):
        res = await join_cmd.execute({})
    assert res.success is False
    assert isinstance(res.next_command, ServerErrorCommand)
