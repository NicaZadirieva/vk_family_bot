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
        vk_name = state.data["vk_name"]
        profile_name = state.data["profile_name"]
        if name:
            state.data["profile_name"] = name
            await self.user_state_service.update_user_state(user_id, state)
            # TODO: добавить переход на генерацию пароля
            return "", ""
        else:
            return MessageTemplates.CHILD_PROFILE_NAME_EMPTY, self.name
