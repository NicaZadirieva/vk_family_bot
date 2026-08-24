from app.core.repositories.base_user_state_repo import IUserStateRepo, UserId, UserState


class InMemoryUserStateRepo(IUserStateRepo):
    def __init__(self) -> None:
        super().__init__()
        self._users_state: dict[UserId, UserState] = {}

    async def clear(self):
        self._users_state.clear()

    async def get_user_state(self, user_id: UserId) -> UserState | None:
        return self._users_state.get(user_id, None)

    async def update_user_state(self, user_id: UserId, new_state: UserState) -> None:
        """
        Обновить состояние пользователя

        Args:
            user_id: ID пользователя
            new_state: Новое состояние
        """
        self._users_state[user_id] = new_state

    async def create_user_state(
        self, user_id: UserId, initial_state: UserState
    ) -> None:
        """
        Создать новое состояние для пользователя

        Args:
            user_id: ID пользователя
            initial_state: Начальное состояние
        """
        self._users_state[user_id] = initial_state

    async def delete_user_state(self, user_id: UserId) -> None:
        """
        Удалить состояние пользователя

        Args:
            user_id: ID пользователя
        """
        if user_id in self._users_state:
            self._users_state.pop(user_id)
