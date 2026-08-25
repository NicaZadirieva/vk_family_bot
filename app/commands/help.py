from app.commands.base import ICommand
from app.core.repositories.base_user_state_repo import UserState
from app.shared.message_templates import MessageTemplates


class HelpCmd(ICommand):
    """
    Помощь
    """

    @property
    def name(self) -> str:
        return "help"

    @property
    def aliases(self) -> list[str]:
        return ["помощь", "помоги", "?"]

    async def execute(
        self,
        user_id: int,
        state: UserState,
        params: str | None = None,
        payload: dict | None = None,
    ) -> tuple[str, str]:
        state.current_screen = "main"
        state.data = {}
        return MessageTemplates.HELP, "main"
