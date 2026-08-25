import logging

from app.commands.base import ICommand
from app.core.di.services_container import ServicesContainer
from app.core.repositories.base_user_state_repo import UserState

logger = logging.getLogger(__name__)


class CreateFamilyCmd(ICommand):
    @property
    def name(self) -> str:
        return "create_family"

    def __init__(self, services: ServicesContainer) -> None:
        self.services = services

    async def execute(
        self,
        user_id: int,
        state: UserState,
        params: str | None = None,
        payload: dict | None = None,
    ) -> tuple[str, str]:
        from app.states.family.create.add_chat_link import AddFamilyChatLinkState

        add_family_chat_link_state = AddFamilyChatLinkState(self.services)
        return await add_family_chat_link_state.enter(user_id, state, payload)
