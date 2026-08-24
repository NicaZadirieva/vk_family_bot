from typing import Any


class AppException(Exception):
    """
    Базовое исключение приложения.

    Attributes:
        message: Сообщение об ошибке
        code: Код ошибки (для API)
        details: Дополнительные детали
        user_message: Сообщение для пользователя
    """

    def __init__(
        self,
        message: str = "Ошибка приложения",
        code: str | None = None,
        details: dict[str, Any] | None = None,
        user_message: str | None = None,
    ):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        self.user_message = user_message or message
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        """Преобразовать исключение в словарь для API."""
        return {
            "error": self.code,
            "message": self.user_message,
            "details": self.details,
        }
