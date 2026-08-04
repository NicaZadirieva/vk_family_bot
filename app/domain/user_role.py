from enum import Enum


class UserRole(Enum):
    """
    Роль юзера приложения (ребенок/родитель)
    """

    CHILD = "CHILD"
    PARENT = "PARENT"
