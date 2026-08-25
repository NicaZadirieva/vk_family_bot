from enum import Enum


class Permission(Enum):
    MASTER = "master"  # Создатель бота
    ADMIN = "admin"  # Может добавлять пользователей
    USER = "user"  # Обычный пользователь
    FAMILY = "family"  # Член семьи (может видеть чат семьи)
