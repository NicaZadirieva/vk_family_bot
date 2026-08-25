from app.core.di.services_container import ServicesContainer
from app.core.repositories.base_user_state_repo import UserState
from app.shared.message_templates import MessageTemplates
from app.states.base import IState
from app.utils.vk_utils import VkUtils


class AddFamilyChatLinkState(IState):
    @property
    def name(self):
        return "add_family_chat_link"

    def __init__(self, services: ServicesContainer):
        self.services = services
        self.user_state_service = self.services.user_state_service()

    async def enter(
        self, user_id: int, state: UserState, payload: dict | None = None
    ) -> tuple[str, str]:
        state.current_screen = self.name
        return MessageTemplates.ASK_CHAT_ID, self.name

    async def handle(
        self, user_id: int, text: str, state: UserState
    ) -> tuple[str, str]:
        chat_id = text.strip()

        # Проверка на корректность VK ID
        if not VkUtils.is_valid_chat_id(chat_id):
            return MessageTemplates.CHILD_VK_CHAT_ID_INVALID, self.name

        # Если проверка пройдена
        # TODO: добавить ссылку в .env
        state.data["chat_link"] = f"https://vk.ru/im/convo/{chat_id}"
        await self.user_state_service.update_user_state(user_id, state)
        from app.states.family.create.add_name import AddFamilyNameState

        add_family_name_state = AddFamilyNameState(self.services)
        return await add_family_name_state.enter(user_id, state)
