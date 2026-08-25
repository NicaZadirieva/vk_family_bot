from app.commands.base import ICommand
from app.core.repositories.base_user_state_repo import UserState


class ProfileKeyboardCommand(ICommand):
    @property
    def name(self) -> str:
        return "profile_kb"

    async def execute(
        self,
        user_id: int,
        state: UserState,
        params: str | None = None,
        payload: dict | None = None,
    ) -> tuple[str, str]:
        state.current_screen = "profile_kb"
        state.data = {}
        # TODO: выделить текстовку
        return "Выберите одно из действий на клавиатуре", "profile_kb"
