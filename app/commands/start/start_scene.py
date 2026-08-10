from enum import Enum, auto

from app.commands.base.base_scene_command import Scene, SceneContext, SceneState
from app.commands.base.scene_result import SceneResult
from app.commands.dependencies import CommandFactory
from app.handlers.session_storage import SessionStorage
from app.services.family_service import FamilyService
from app.services.login_service import LoginService
from app.services.password_service import PasswordService


class StartStep(Enum):
    """Шаги создания семьи"""

    GET_FAMILY = auto()  # проверить есть ли у чата зарегестрированная семья
    GET_USER_INSIDE_FAMILY = auto()  # проверить зарегестрирован ли в семье данный юзер
    ASK_PASSWORD = auto()  # Спросить пароль у юзера, если не авторизован
    FORBIDDEN = auto()  # запрет доступа если нет пароля
    ASK_CREATE_FAMILY = auto()  # предложить создать семью
    CONFIRM = auto()  # Подтверждение
    COMPLETED = auto()  # Завершено


class StartScene(Scene):
    """Сцена начала работы с ботом"""

    def __init__(
        self,
        password_service: PasswordService,
        family_service: FamilyService,
        login_service: LoginService,
        session: SessionStorage,
        command_factory: CommandFactory,
    ):
        super().__init__("start_scene")
        self._family_service = family_service
        self._login_service = login_service
        self.session = session
        self._password_service = password_service
        self.command_factory = command_factory

    # 1 есть ли у чата зарегестрированная семья
    # 2 если есть -> зарегестрирован ли вошедший в бота
    # 2 если нет -> есть ли добавленный для текущего vk_id пароль
    # 	2.1 если есть -> предложить ввести пароль
    #   2.2 если нет -> запрет доступа
    # 3 если не существует -> предложить создать семью (CreateFamilyCmd)

    async def on_enter(self, vk_id: int, context: SceneContext) -> SceneResult:
        """Вход в сцену"""
        context.data = {"family": {}, "parent": {}, "children": []}
        context.step = StartStep.GET_FAMILY
        context.state = SceneState.WAITING_INPUT
        context.vk_id = vk_id

        return SceneResult(
            completed=False,
            message=(
                "👨‍👩‍👧‍👦 **Добро пожаловать в бот**\n\n"
                "Давайте проверим вашу ссылку на чат семьи!\n"
                "Пожалуйста, введите ссылку:"
            ),
            next_command=None,
        )

    async def on_message(
        self, vk_id: int, text: str, context: SceneContext
    ) -> SceneResult:
        """Обработка сообщений в сцене"""

        # Проверка на отмену
        if text.lower() in ["/cancel", "отмена", "cancel"]:
            context.state = SceneState.CANCELLED
            return SceneResult(
                completed=True, message="❌ Вход в бота отменен", next_command=None
            )

        step = context.step
        if step == StartStep.GET_FAMILY:
            # Шаг 1 есть ли у чата зарегестрированная семья:
            # https://vk.ru/im/convo/223232323?entrypoint=list_all
            link = text.split("/convo/")[1].split("?entrypoint")[0]
            family = await self._family_service.search_family_by_link(link)
            if family:
                auth_user = await self._login_service.search_register_user(
                    vk_id, family.id
                )
                if auth_user:
                    return SceneResult(
                        completed=True,
                        message="Вы уже зарегестрированы в бота. Ниже справка по командам",
                        next_command=self.command_factory.get_command("help"),
                    )
                else:
                    return SceneResult(
                        completed=True,
                        message="Вы не авторизованы",
                        next_command=self.command_factory.get_command("join"),
                    )
            else:
                return SceneResult(
                    completed=True,
                    message="Такая семья не существует в базе",
                    next_command=self.command_factory.get_command("create_family"),
                )

        return SceneResult(
            completed=True,
            message="⚠️ Произошла ошибка. Попробуйте позже.",
            next_command=self.command_factory.get_command("error"),
        )

    async def on_exit(self, vk_id: int, context: SceneContext) -> str:
        """
        Выход из сцены.
        Вызывается при завершении или отмене сцены.
        """
        return "👋 До свидания!"
