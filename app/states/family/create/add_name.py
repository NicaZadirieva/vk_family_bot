from app.core.di.services_container import ServicesContainer
from app.core.repositories.base_user_state_repo import UserState
from app.shared.message_templates import MessageTemplates
from app.states.base import IState


class AddFamilyNameState(IState):
    @property
    def name(self):
        return "add_family_name"

    def __init__(self, services: ServicesContainer):
        self.services = services
        self.user_state_service = self.services.user_state_service()

    async def enter(
        self, user_id: int, state: UserState, payload: dict | None = None
    ) -> tuple[str, str]:
        state.current_screen = self.name
        return "Введите название для Вашей семьи", self.name

    async def handle(
        self, user_id: int, text: str, state: UserState
    ) -> tuple[str, str]:
        family_name = text.strip()
        if family_name:
            state.data["family_name"] = family_name
            await self.user_state_service.update_user_state(user_id, state)
            # TODO: сохранить семью
            return MessageTemplates.FAMILY_CREATED, "main"
        else:
            return "❌ Введите название для Вашей семьи", self.name
