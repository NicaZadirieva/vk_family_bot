from typing import Any

from app.exceptions.app_exception import AppException


class DatabaseError(AppException):
    """Ошибка базы данных."""

    def __init__(
        self,
        message: str,
        code: str = "DATABASE_ERROR",
        details: dict[str, Any] | None = None,
        user_message: str | None = None,
    ):
        super().__init__(
            message=message,
            code=code,
            details=details,
            user_message=user_message or "Произошла ошибка при работе с базой данных",
        )
