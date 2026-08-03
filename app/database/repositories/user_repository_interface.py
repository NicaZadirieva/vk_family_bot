from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")


class IUserRepository[T](ABC):
    """Base repo"""

    @abstractmethod
    async def search_user(self, user_id: int, family_id: int):
        pass
