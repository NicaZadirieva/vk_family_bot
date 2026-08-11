import logging
from typing import Optional

from app.commands.base.base_command import Command
from app.commands.base.command_result import CommandResult
from app.commands.dependencies import CommandFactory
from app.commands.help.help_command import HelpCommand
from app.commands.start.start_scene import StartScene
from app.core.session.session_service import SessionService
from app.services.family_service import FamilyService
from app.services.login_service import LoginService
from app.services.password_service import PasswordService

logger = logging.getLogger(__name__)


class StartCommand(Command):
    """
    Команда для старта работы с ботом.

    Обрабатывает:
    - Начало новой сессии
    - Продолжение прерванной сцены
    - Вход в семью через ссылку и пароль
    """

    def __init__(
        self,
        family_service: FamilyService,
        login_service: LoginService,
        password_service: PasswordService,
        session_service: SessionService,
        command_factory: CommandFactory,
    ):
        """
        Args:
            family_service: Сервис для работы с семьями
            login_service: Сервис для работы с логином
            password_service: Сервис для работы с паролями
            session_service: Сервис для управления сессиями
            command_factory: Фабрика команд

        Raises:
            ValueError: Если обязательные зависимости не переданы
        """
        super().__init__()

        # Валидация зависимостей
        if not family_service:
            raise ValueError("family_service is required")
        if not login_service:
            raise ValueError("login_service is required")
        if not password_service:
            raise ValueError("password_service is required")
        if not session_service:
            raise ValueError("session_service is required")
        if not command_factory:
            raise ValueError("command_factory is required")

        self._family_service = family_service
        self._login_service = login_service
        self._password_service = password_service
        self._session_service = session_service
        self._command_factory = command_factory

        # Создаем сцену
        self._scene = StartScene(
            family_service=family_service,
            login_service=login_service,
            password_service=password_service,
            session_service=session_service,
            command_factory=command_factory,
        )

    def get_help_command(self) -> HelpCommand:
        """Возвращает справку по команде."""
        return (
            HelpCommand()
            .for_command("start")
            .with_description("Старт бота")
            .with_usage("/start")
            .with_example("/start")
            .with_notes("Начинает диалог с ботом")
        )

    async def execute(self, vk_id: int, text: str) -> CommandResult:
        """
        Выполняет команду start.

        Args:
            vk_id: ID пользователя ВКонтакте
            text: Текст сообщения

        Returns:
            CommandResult: Результат выполнения команды
        """
        try:
            # Проверяем, есть ли активная сессия
            session = await self._session_service.get_session(vk_id)
            is_in_scene = session and session.state == "start_scene"

            # Обработка активной сцены
            if is_in_scene:
                return await self._handle_active_scene(vk_id, text)

            # Запуск новой сцены
            if text == "/start" or text == "/start@bot":
                return await self._start_new_scene(vk_id)

            # Пользователь не в сцене и не ввел /start
            return CommandResult.failure(
                error="Используйте команду /start для входа в бота",
                next_command=self.get_help_command(),
            )

        except Exception as e:
            logger.error(f"Unexpected error in StartCommand: {e}", exc_info=True)
            return CommandResult.failure(
                error="Произошла ошибка. Попробуйте позже.",
                next_command=self.get_help_command(),
            )

    async def _handle_active_scene(self, vk_id: int, text: str) -> CommandResult:
        """
        Обрабатывает активную сцену пользователя.

        Args:
            vk_id: ID пользователя
            text: Текст сообщения

        Returns:
            CommandResult: Результат обработки
        """
        try:
            # Проверка на отмену
            if text.lower() in ["/cancel", "отмена", "cancel"]:
                await self._scene.cancel(vk_id)
                await self._session_service.update_state(vk_id, "idle")
                return CommandResult.success(
                    message="❌ Действие отменено", data={"cancelled": True}
                )

            # Продолжаем сцену
            result = await self._scene.process_message(vk_id, text)

            # Отправляем ответ пользователю
            if result.message:
                await self._send_message(vk_id, result.message)

            # Сцена завершена
            if result.completed:
                await self._scene.exit(vk_id)
                await self._session_service.update_state(vk_id, "idle")

                # Если сцена вернула следующую команду
                if result.next_command:
                    return CommandResult.success(
                        message=result.message,
                        data={"completed": True},
                        next_command=result.next_command,
                    )

                return CommandResult.success(
                    message=result.message, data={"completed": True}
                )

            # Сцена продолжается
            return CommandResult.success(
                message=result.message, data={"scene_active": True}
            )

        except Exception as e:
            logger.error(f"Error in scene processing: {e}", exc_info=True)
            await self._scene.exit(vk_id)
            await self._session_service.update_state(vk_id, "idle")
            return CommandResult.failure(
                error="Ошибка обработки сцены", next_command=self.get_help_command()
            )

    async def _start_new_scene(self, vk_id: int) -> CommandResult:
        """
        Запускает новую сцену для пользователя.

        Args:
            vk_id: ID пользователя

        Returns:
            CommandResult: Результат запуска
        """
        try:
            # Начинаем новую сессию
            await self._session_service.create_session(
                vk_id, initial_state="start_scene"
            )

            # Запускаем сцену
            result = await self._scene.enter(vk_id)

            # Отправляем приветствие
            if result.message:
                await self._send_message(vk_id, result.message)

            return CommandResult.success(
                message=result.message, data={"scene_started": True}
            )

        except Exception as e:
            logger.error(f"Error starting scene: {e}", exc_info=True)
            await self._session_service.clear_session(vk_id)
            return CommandResult.failure(
                error="Не удалось начать диалог", next_command=self.get_help_command()
            )

    async def _send_message(self, vk_id: int, text: str) -> None:
        """
        Отправляет сообщение пользователю.

        Args:
            vk_id: ID пользователя
            text: Текст сообщения
        """
        # TODO: Реализовать реальную отправку через VK API
        logger.info(f"Sending message to {vk_id}: {text[:50]}...")
        print(f"Сообщение для {vk_id}: {text}")
        # await vk_api.messages.send(user_id=vk_id, message=text)
