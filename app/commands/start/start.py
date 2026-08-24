from app.states.main_state import MainState

from app.commands.base import ICommand
from app.core.repositories.base_user_state_repo import UserState


class StartCommand(ICommand):
    @property
    def name(self) -> str:
        return "start"

    async def execute(
        self, user_id: int, state: UserState, payload: dict | None = None
    ) -> tuple[str, str]:
        main_state = MainState()
        state.current_screen = main_state.name
        return await main_state.enter(user_id, state)
