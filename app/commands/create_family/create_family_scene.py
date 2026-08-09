from enum import Enum, auto

from app.commands.base.base_scene_command import Scene, SceneContext, SceneState
from app.handlers.session_storage import SessionStorage


class CreateFamilyStep(Enum):
    """Шаги создания семьи"""

    ASK_NAME = auto()  # Спросить название семьи
    ASK_PARENT = auto()  # Спросить данные родителя
    ASK_CHILD = auto()  # Спросить данные ребенка
    CONFIRM = auto()  # Подтверждение
    COMPLETED = auto()  # Завершено


class CreateFamilyScene(Scene):
    """Сцена создания новой семьи"""

    def __init__(self, session: SessionStorage):
        super().__init__("create_family")
        self.session = session

    async def on_enter(self, user_id: int, context: SceneContext) -> str:
        """Вход в сцену"""
        context.data = {"family": {}, "parent": {}, "children": []}
        context.step = CreateFamilyStep.ASK_NAME
        context.state = SceneState.WAITING_INPUT
        context.user_id = user_id

        return (
            "👨‍👩‍👧‍👦 **Создание новой семьи**\n\n"
            "Давайте создадим вашу семью!\n"
            "Пожалуйста, введите название семьи:"
        )

    async def on_message(self, user_id: int, text: str, context: SceneContext):
        """Обработка сообщений в сцене"""

        # Проверка на отмену
        if text.lower() in ["/cancel", "отмена", "cancel"]:
            context.state = SceneState.CANCELLED
            return True, "❌ Создание семьи отменено."

        step = context.step

        # Шаг 1: Название семьи
        if step == CreateFamilyStep.ASK_NAME:
            if len(text.strip()) < 2:
                return (
                    False,
                    (
                        "❌ Название семьи должно содержать минимум 2 символа.\n"
                        "Попробуйте снова:"
                    ),
                )

            context.data["family"]["name"] = text.strip()
            context.step = CreateFamilyStep.ASK_PARENT

            return (
                False,
                (
                    f"✅ Отлично! Семья '{text.strip()}' будет создана.\n\n"
                    f"Теперь укажите имя родителя (папы или мамы):"
                ),
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

    async def _show_confirmation(self, context: SceneContext) -> tuple:
        """Показать подтверждение данных"""
        family_name = context.data["family"]["name"]
        parent_name = context.data["parent"]["name"]
        children = context.data["children"]
        children_count = len(children)
        children_list = ", ".join(children) if children else "нет"

        return (
            False,
            (
                f"📋 **Проверьте данные семьи:**\n\n"
                f"🏠 Название: {family_name}\n"
                f"👤 Родитель: {parent_name}\n"
                f"👶 Детей: {children_count}\n"
                f"📋 Список: {children_list}\n\n"
                f"✅ Всё верно? (да/нет)"
            ),
        )

    async def on_exit(self, user_id: int, context: SceneContext) -> str:
        """
        Выход из сцены.
        Вызывается при завершении или отмене сцены.
        """
        if context.state == SceneState.COMPLETED:
            # Успешное завершение
            family_name = context.data.get("family", {}).get("name", "семья")
            children_count = len(context.data.get("children", []))

            return (
                f"👋 До свидания! Семья '{family_name}' успешно создана.\n"
                f"В семье {children_count + 1} человек.\n\n"
                f"💡 Совет: используйте команду /my_family чтобы посмотреть информацию о семье."
            )

        elif context.state == SceneState.CANCELLED:
            # Отмена сцены
            return (
                "❌ Создание семьи отменено.\n\n"
                "💡 Если передумаете, введите /create_family чтобы начать заново."
            )

        else:
            # Другие случаи выхода
            return (
                "👋 Выход из сцены создания семьи.\n\n"
                "💡 Для создания новой семьи введите /create_family"
            )

    async def _show_completion(self, context: SceneContext) -> str:
        """Показать завершение"""
        family_name = context.data["family"]["name"]
        children_count = len(context.data["children"])

        return (
            f"🎉 **Семья '{family_name}' успешно создана!**\n\n"
            f"👨‍👩‍👧‍👦 В семье {children_count + 1} человек\n"
            f"👶 Детей: {children_count}\n\n"
            f"✅ Вы можете использовать команды для управления семьей."
        )

    async def _save_family(self, context: SceneContext):
        """Сохранить данные семьи в хранилище"""
        # Сохраняем в сессию
        self.session.set_multiple(
            {
                "family_name": context.data["family"]["name"],
                "parent_name": context.data["parent"]["name"],
                "children": context.data["children"],
            }
        )

        # Здесь можно добавить сохранение в БД
        # await save_to_database(context.data)
