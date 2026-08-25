from app.core.di.services_container import ServicesContainer
from app.core.repositories.base_user_state_repo import UserState
from app.shared.message_templates import MessageTemplates
from app.states.base import IState
from app.utils.vk_utils import VkUtils


class AddChildVkNameState(IState):
    def __init__(self, services: ServicesContainer):
        self.services = services
        self.user_state_service = self.services.user_state_service()

    @property
    def name(self) -> str:
        return "add_child_vk_name"

    async def enter(
        self, user_id: int, state: UserState, payload: dict | None = None
    ) -> tuple[str, str]:
        state.current_screen = self.name
        return MessageTemplates.ASK_CHILD_VK_NAME, self.name

    async def handle(
        self, user_id: int, text: str, state: UserState
    ) -> tuple[str, str]:
        name = text.strip()

        # Проверка на корректность VK ID
        if not VkUtils.is_valid_vk_id(name):
            return MessageTemplates.CHILD_VK_NAME_INVALID, self.name

        # Если проверка пройдена
        state.data["vk_name"] = name
        await self.user_state_service.update_user_state(user_id, state)
        from .add_child_user_profile import AddChildUserProfileState

        child_user_profile_state = AddChildUserProfileState(self.services)
        return await child_user_profile_state.enter(user_id, state)
