from app.commands.base import ICommand
from app.core.repositories.base_user_state_repo import UserState
from app.shared.message_templates import MessageTemplates


class ProfileKeyboardCommand(ICommand):
    @property
    def name(self) -> str:
        return "profile_kb"

    async def execute(
        self, user_id: int, state: UserState, payload: dict | None = None
    ) -> tuple[str, str]:
        state.current_screen = "profile_kb"
        state.data = {}
        return "Выберите одно из действий на клавиатуре", "profile_kb"
