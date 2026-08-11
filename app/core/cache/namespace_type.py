from enum import Enum


class NamespaceType(Enum):
    """Типы пространств имен."""

    GLOBAL = "global"
    USER = "user"
    FAMILY = "family"
