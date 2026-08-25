from app.core.di.services_container import ServicesContainer
from app.core.repositories.base_user_state_repo import UserState
from app.shared.message_templates import MessageTemplates
from app.states.base import IState


class AddChildUserProfileState(IState):
    def __init__(self, services: ServicesContainer):
        self.services = services
        self.user_state_service = self.services.user_state_service()

    @property
    def name(self) -> str:
        return "add_child_user_profile"

    async def enter(
        self, user_id: int, state: UserState, payload: dict | None = None
    ) -> tuple[str, str]:
        state.current_screen = self.name
        return MessageTemplates.ASK_CHILD_PROFILE_NAME, self.name

    async def handle(
        self, user_id: int, text: str, state: UserState
    ) -> tuple[str, str]:
        name = text.strip()
        if name:
            state.data["profile_name"] = name
            await self.user_state_service.update_user_state(user_id, state)
            from app.states.add.generate_child_password import (
                GenerateChildPasswordState,
            )

            generate_child_password_state = GenerateChildPasswordState(
                services=self.services
            )
            return await generate_child_password_state.enter(user_id, state)
        else:
            return MessageTemplates.CHILD_PROFILE_NAME_EMPTY, self.name
