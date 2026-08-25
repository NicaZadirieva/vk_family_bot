import re

from app.commands.base import ICommand
from app.core.di.services_container import ServicesContainer
from app.core.repositories.base_user_state_repo import UserState
from app.states.add.generate_child_password import GenerateChildPasswordState


class AddChildCmd(ICommand):
    """
    Приглашение других детей происходит по команде /add_child @ИмяВК [Имя_профиля].
    Бот проверяет, что этот VK ID не состоит в другой семье и что пользователь с таким VK_ID существует в VK,
    если это так, генерирует 6-значный код.
    При ошибке проверки — отказывать в генерации кода с сообщением о технической проблеме.
    """

    def __init__(self, services: ServicesContainer):
        self.services = services
        self.user_state_service = self.services.user_state_service()

    @property
    def name(self) -> str:
        return "add_child"

    def _parse_params(self, params: str) -> tuple[str | None, str | None]:
        """
        Парсит параметры команды /add_child.
        Формат: /add_child @ИмяВК [Имя_профиля]
        Или: /add_child vk_id [Имя_профиля]

        Возвращает: (vk_identifier, profile_name) или (None, None) при ошибке
        """
        if not params or not params.strip():
            return None, None

        params = params.strip()

        # Ищем имя профиля в квадратных скобках
        bracket_pattern = r"\[([^\]]+)\]"
        bracket_match = re.search(bracket_pattern, params)

        if not bracket_match:
            return None, None  # Нет квадратных скобок - ошибка

        profile_name = bracket_match.group(1).strip()

        if not profile_name:
            return None, None  # Пустое имя в скобках

        # Все что до скобок - VK идентификатор
        vk_part = params[: bracket_match.start()].strip()

        if not vk_part:
            return None, None  # Нет VK идентификатора

        # Убираем @ если есть
        vk_part = vk_part.removeprefix("@")

        return vk_part, profile_name

    async def execute(
        self,
        user_id: int,
        state: UserState,
        params: str | None = None,
        payload: dict | None = None,
    ) -> tuple[str, str]:

        # Парсим параметры
        generate_child_password_state = GenerateChildPasswordState(self.services)
        if params:
            vk_identifier, profile_name = self._parse_params(params or "")

            if not vk_identifier or not profile_name:
                # TODO: подумать надо ли добавлять в MessageTemplates
                return (
                    "❌ Неверный формат команды!\n"
                    "Используйте: /add_child @ИмяВК [Имя_профиля]\n"
                    "Например: /add_child @ivanov [Петр Иванов]"
                ), self.name
            # TODO:
            # 1. Проверить, что VK ID не состоит в другой семье
            # 2. Проверить, что пользователь с таким VK ID существует в VK
            # 3. Если все ок, сгенерировать 6-значный код
            state.data["vk_name"] = vk_identifier
            state.data["profile_name"] = profile_name
            await self.user_state_service.update_user_state(user_id, new_state=state)
            return await generate_child_password_state.enter(user_id, state, payload)
        else:
            return await generate_child_password_state.enter(user_id, state, payload)
