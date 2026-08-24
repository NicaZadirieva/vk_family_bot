from app.core.repositories.base_user_state_repo import IUserStateRepo, UserId, UserState


class UserStateService:
    """Сервис для работы с состояниями пользователей"""

    def __init__(self, repository: IUserStateRepo):
        self._repo = repository

    async def get_user_state(self, user_id: UserId) -> UserState | None:
        """
        Получить состояние пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Состояние пользователя или None, если не найдено
        """
        return await self._repo.get_user_state(user_id)

    async def update_user_state(self, user_id: UserId, new_state: UserState) -> None:
        """
        Обновить состояние пользователя

        Args:
            user_id: ID пользователя
            new_state: Новое состояние
        """
        await self._repo.update_user_state(user_id, new_state)

    async def create_user_state(
        self, user_id: UserId, initial_state: UserState
    ) -> None:
        """
        Создать новое состояние для пользователя

        Args:
            user_id: ID пользователя
            initial_state: Начальное состояние
        """
        await self._repo.create_user_state(user_id, initial_state)

    async def delete_user_state(self, user_id: UserId) -> None:
        """
        Удалить состояние пользователя

        Args:
            user_id: ID пользователя
        """
        await self._repo.delete_user_state(user_id)

    async def get_or_create_user_state(
        self, user_id: UserId, default_state: UserState
    ) -> UserState:
        """
        Получить состояние пользователя или создать новое с дефолтным значением

        Args:
            user_id: ID пользователя
            default_state: Состояние по умолчанию

        Returns:
            Состояние пользователя
        """
        state = await self._repo.get_user_state(user_id)
        if state is None:
            await self._repo.create_user_state(user_id, default_state)
            return default_state
        return state

    async def update_user_state_if_exists(
        self, user_id: UserId, new_state: UserState
    ) -> bool:
        """
        Обновить состояние пользователя, если оно существует

        Args:
            user_id: ID пользователя
            new_state: Новое состояние

        Returns:
            True если обновление выполнено, False если состояние не найдено
        """
        existing = await self._repo.get_user_state(user_id)
        if existing is None:
            return False

        await self._repo.update_user_state(user_id, new_state)
        return True

    async def clear_all_states(self) -> None:
        """Очистить все состояния (для тестирования)"""
        await self._repo.clear_all_states()

    async def user_state_exists(self, user_id: UserId) -> bool:
        """
        Проверить, существует ли состояние для пользователя

        Args:
            user_id: ID пользователя

        Returns:
            True если состояние существует, иначе False
        """
        state = await self._repo.get_user_state(user_id)
        return state is not None
