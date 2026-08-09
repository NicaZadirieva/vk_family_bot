from enum import Enum, auto

from app.commands.base.base_scene_command import Scene, SceneContext, SceneState
from app.commands.base.scene_result import SceneResult
from app.commands.create_family.create_family_cmd import CreateFamilyCmd
from app.handlers.session_storage import SessionStorage
from app.services.family_service import FamilyService


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

    def __init__(self, family_service: FamilyService, session: SessionStorage):
        super().__init__("start_scene")
        self._family_service = family_service
        self.session = session

    # 1 есть ли у чата зарегестрированная семья
    # 2 если есть -> зарегестрирован ли вошедший в бота
    # 2 если нет -> есть ли добавленный для текущего vk_id пароль
    # 	2.1 если есть -> предложить ввести пароль
    #   2.2 если нет -> запрет доступа
    # 3 если не существует -> предложить создать семью (CreateFamilyCmd)

    async def on_enter(self, user_id: int, context: SceneContext) -> SceneResult:
        """Вход в сцену"""
        context.data = {"family": {}, "parent": {}, "children": []}
        context.step = StartStep.GET_FAMILY
        context.state = SceneState.WAITING_INPUT
        context.user_id = user_id

        return SceneResult(
            completed=False,
            message=(
                "👨‍👩‍👧‍👦 **Добро пожаловать в бот**\n\n"
                "Давайте проверим вашу ссылку на чат семьи!\n"
                "Пожалуйста, введите ссылку:"
            ),
            next_command=None,
        )

    async def on_message(self, user_id: int, text: str, context: SceneContext):
        """Обработка сообщений в сцене"""

        # Проверка на отмену
        if text.lower() in ["/cancel", "отмена", "cancel"]:
            context.state = SceneState.CANCELLED
            return True, "❌ Создание семьи отменено."

        step = context.step
        if step == StartStep.GET_FAMILY:
            # Шаг 1 есть ли у чата зарегестрированная семья:
            # https://vk.ru/im/convo/223232323?entrypoint=list_all
            link = text.split("/convo/")[1].split("?entrypoint")[0]
            family = await self._family_service.search_family_by_link(link)
            if family:
                pass
            else:
                return SceneResult(
                    completed=True,
                    message="Такая семья не существует в базе",
                    next_command=CreateFamilyCmd(self.session),
                )

        # Шаг 2: Имя родителя
        elif step == CreateFamilyStep.ASK_PARENT:
            if len(text.strip()) < 2:
                return (
                    False,
                    "❌ Имя должно содержать минимум 2 символа.\nПопробуйте снова:",
                )

            context.data["parent"]["name"] = text.strip()
            context.step = CreateFamilyStep.ASK_CHILD

            return (
                False,
                (
                    f"✅ Родитель: {text.strip()}\n\n"
                    f"👶 Теперь добавьте первого ребенка.\n"
                    f"Введите имя ребенка или напишите 'пропустить', если детей нет:"
                ),
            )

        # Шаг 3: Добавление детей
        elif step == CreateFamilyStep.ASK_CHILD:
            if text.lower() == "пропустить":
                # Переходим к подтверждению
                context.step = CreateFamilyStep.CONFIRM

                return await self._show_confirmation(context)

            if len(text.strip()) < 2:
                return (
                    False,
                    (
                        "❌ Имя ребенка должно содержать минимум 2 символа.\n"
                        "Попробуйте снова:"
                    ),
                )

            # Добавляем ребенка
            context.data["children"].append(text.strip())

            children_count = len(context.data["children"])
            children_names = ", ".join(context.data["children"])

            return (
                False,
                (
                    f"✅ Добавлен ребенок: {text.strip()}\n\n"
                    f"👶 Всего детей: {children_count}\n"
                    f"📋 Список: {children_names}\n\n"
                    f"Хотите добавить еще ребенка?\n"
                    f"Введите имя или напишите 'готово' для завершения:"
                ),
            )

        # Шаг 4: Завершение добавления детей
        elif step == CreateFamilyStep.CONFIRM:
            if text.lower() in ["готово", "да", "yes"]:
                # Сохраняем данные
                context.state = SceneState.COMPLETED

                # Здесь сохраняем в БД
                await self._save_family(context)

                return True, await self._show_completion(context)
            elif text.lower() in ["нет", "no"]:
                # Возвращаемся к добавлению детей
                context.step = CreateFamilyStep.ASK_CHILD
                return False, "👶 Введите имя ребенка или напишите 'пропустить':"
            else:
                return False, "❓ Пожалуйста, ответьте 'да' или 'нет':"

        return True, "⚠️ Произошла ошибка. Попробуйте позже."
