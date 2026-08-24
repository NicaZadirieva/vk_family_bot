from abc import ABC, abstractmethod

UserId = int
"""
Id пользователя в кэше
"""


class UserState:
    """
    Состояние пользователя
    """

    def __init__(self, user_id: UserId):
        self.user_id = user_id
        self.current_screen: str = "main"
        self.data = {}


class IUserStateRepo(ABC):
    @abstractmethod
    async def clear_all_states(self) -> None:
        """Очистить все состояния (для тестирования)"""

    @abstractmethod
    async def get_user_state(self, user_id: UserId) -> UserState | None:
        """
        Получить состояние конкретного юзера по Id
        """

    @abstractmethod
    async def update_user_state(self, user_id: UserId, new_state: UserState) -> None:
        """
        Обновить состояние пользователя

        Args:
            user_id: ID пользователя
            new_state: Новое состояние
        """

    @abstractmethod
    async def create_user_state(
        self, user_id: UserId, initial_state: UserState
    ) -> None:
        """
        Создать новое состояние для пользователя

        Args:
            user_id: ID пользователя
            initial_state: Начальное состояние
        """

    @abstractmethod
    async def delete_user_state(self, user_id: UserId) -> None:
        """
        Удалить состояние пользователя

        Args:
            user_id: ID пользователя
        """
