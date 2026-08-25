import random

from app.core.di.services_container import ServicesContainer
from app.core.repositories.base_user_state_repo import UserState
from app.shared.message_templates import MessageTemplates
from app.states.base import IState


class GenerateChildPasswordState(IState):
    def __init__(self, services: ServicesContainer):
        self.services = services

    @property
    def name(self) -> str:
        return "generate_child_password"

    async def enter(
        self, user_id: int, state: UserState, payload: dict | None = None
    ) -> tuple[str, str]:
        state.current_screen = self.name
        return (
            f"Создаю пароль для пользователя {state.data.get('vk_name', '')}",
            self.name,
        )

    async def handle(
        self, user_id: int, text: str, state: UserState
    ) -> tuple[str, str]:
        vk_name = state.data.get("vk_name")
        profile_name = state.data.get("profile_name")

        if vk_name and profile_name:
            # Генерация 6-значного пароля (цифры + буквы)
            password = self._generate_password()

            # Сохраняем пароль в состояние
            state.data["child_password"] = password

            # TODO: вызов сервиса InviteService с сохранением кода

            # Формируем сообщение с паролем (инвайт-кодом)
            message = MessageTemplates.INVITE_CODE.format(code=password)

            return message, self.name
        else:
            return MessageTemplates.GENERATE_INVITE_CODE_NO_NAMES, self.name

    def _generate_password(self) -> str:
        """
        Генерирует 6-значный пароль, состоящий из цифр и букв (латиница).
        Для удобства использования исключены похожие символы: 0, O, 1, l, I
        """
        # Набор символов: цифры (без 0,1) + буквы (без O,o,I,i,l)
        chars = "23456789abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ"

        # Генерируем пароль длиной 6 символов
        password = "".join(random.choice(chars) for _ in range(6))

        return password
