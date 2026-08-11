import logging
from enum import Enum, auto
from typing import Optional

from app.commands.base.base_scene_command import Scene, SceneResult
from app.commands.dependencies import CommandFactory
from app.core.session.session_service import SessionService
from app.services.family_service import FamilyService
from app.services.login_service import LoginService
from app.services.password_service import PasswordService

logger = logging.getLogger(__name__)


class StartStep(Enum):
    """Шаги сцены."""

    ENTER_LINK = auto()
    ENTER_PASSWORD = auto()
    COMPLETED = auto()


class StartScene(Scene):
    """Сцена начала работы с ботом."""

    def __init__(
        self,
        family_service: FamilyService,
        login_service: LoginService,
        password_service: PasswordService,
        session_service: SessionService,
        command_factory: CommandFactory,
    ):
        super().__init__("start_scene")
        self._family_service = family_service
        self._login_service = login_service
        self._password_service = password_service
        self._session_service = session_service
        self._command_factory = command_factory

    async def enter(self, vk_id: int) -> SceneResult:
        """Вход в сцену."""
        # Сохраняем состояние в сессии
        session = await self._session_service.get_session(vk_id)
        if session:
            session.scene_data = {"step": StartStep.ENTER_LINK.name, "attempts": 0}
            await self._session_service.save_session(session)

        return SceneResult(
            completed=False,
            message=(
                "👨‍👩‍👧‍👦 **Добро пожаловать в бот**\n\n"
                "Давайте проверим вашу ссылку на чат семьи!\n"
                "Пожалуйста, введите ссылку:"
            ),
            next_command=None,
        )

    async def process_message(self, vk_id: int, text: str) -> SceneResult:
        """Обрабатывает сообщение в сцене."""
        # Получаем сессию
        session = await self._session_service.get_session(vk_id)
        if not session:
            return SceneResult(
                completed=True,
                message="⚠️ Сессия не найдена. Попробуйте /start",
                next_command=self._command_factory.get_command("help"),
            )

        step = session.scene_data.get("step")

        if step == StartStep.ENTER_LINK.name:
            return await self._handle_link_input(vk_id, text)

        if step == StartStep.ENTER_PASSWORD.name:
            return await self._handle_password_input(vk_id, text)

        return SceneResult(
            completed=True,
            message="⚠️ Произошла ошибка. Попробуйте позже.",
            next_command=self._command_factory.get_command("help"),
        )

    async def _handle_link_input(self, vk_id: int, text: str) -> SceneResult:
        """Обрабатывает ввод ссылки."""
        try:
            # Извлекаем ID чата из ссылки
            # Пример: https://vk.ru/im/convo/123456?entrypoint=list_all
            if "/convo/" in text:
                chat_id = text.split("/convo/")[1].split("?")[0]
            else:
                # Пробуем другие форматы
                chat_id = text.strip()

            # Ищем семью
            family = await self._family_service.search_family_by_link(chat_id)

            if family:
                # Проверяем авторизацию
                user = await self._login_service.search_register_user(vk_id, family.id)

                if user:
                    # Уже авторизован
                    await self._session_service.clear_session(vk_id)
                    return SceneResult(
                        completed=True,
                        message="✅ Вы уже зарегистрированы в боте!",
                        next_command=self._command_factory.get_command("help"),
                    )
                else:
                    # Запрашиваем пароль
                    session = await self._session_service.get_session(vk_id)
                    if session:
                        session.scene_data["step"] = StartStep.ENTER_PASSWORD.name
                        session.scene_data["family_id"] = family.id
                        session.scene_data["link"] = chat_id
                        await self._session_service.save_session(session)

                    return SceneResult(
                        completed=False,
                        message="🔑 Введите секретный пароль для входа в семью:",
                        next_command=None,
                    )
            else:
                # Семья не найдена
                await self._session_service.clear_session(vk_id)
                return SceneResult(
                    completed=True,
                    message="🏠 Семья не найдена. Создайте новую семью!",
                    next_command=self._command_factory.get_command("create_family"),
                )

        except Exception as e:
            logger.error(f"Error parsing link: {e}", exc_info=True)
            return SceneResult(
                completed=False,
                message="❌ Неверный формат ссылки. Попробуйте еще раз:",
                next_command=None,
            )

    async def _handle_password_input(self, vk_id: int, text: str) -> SceneResult:
        """Обрабатывает ввод пароля."""
        try:
            # Получаем данные из сессии
            session = await self._session_service.get_session(vk_id)
            if not session:
                return SceneResult(
                    completed=True,
                    message="⚠️ Сессия не найдена",
                    next_command=self._command_factory.get_command("help"),
                )

            family_id = session.scene_data.get("family_id")
            if not family_id:
                return SceneResult(
                    completed=True,
                    message="⚠️ Ошибка: семья не найдена",
                    next_command=self._command_factory.get_command("help"),
                )

            is_valid = await self._password_service.verify_user(
                vk_id=vk_id, family_id=family_id, password=text,
                family_id=family_id
            )

            if is_valid:
                # Успешный вход
                await self._session_service.clear_session(vk_id)
                return SceneResult(
                    completed=True,
                    message="✅ Вы успешно вошли в семью!",
                    next_command=self._command_factory.get_command("help"),
                )
            else:
                # Неверный пароль
                attempts = session.scene_data.get("attempts", 0) + 1
                session.scene_data["attempts"] = attempts
                await self._session_service.save_session(session)

                if attempts >= 3:
                    # Превышено количество попыток
                    await self._session_service.clear_session(vk_id)
                    return SceneResult(
                        completed=True,
                        message="❌ Превышено количество попыток. Попробуйте /start",
                        next_command=self._command_factory.get_command("start"),
                    )

                return SceneResult(
                    completed=False,
                    message=f"❌ Неверный пароль. Осталось попыток: {3 - attempts}",
                    next_command=None,
                )

        except Exception as e:
            logger.error(f"Error handling password: {e}", exc_info=True)
            return SceneResult(
                completed=True,
                message="⚠️ Произошла ошибка. Попробуйте позже.",
                next_command=self._command_factory.get_command("help"),
            )

    async def exit(self, vk_id: int) -> None:
        """Выход из сцены."""
        await self._session_service.clear_session(vk_id)

    async def cancel(self, vk_id: int) -> None:
        """Отмена сцены."""
        await self._session_service.clear_session(vk_id)
