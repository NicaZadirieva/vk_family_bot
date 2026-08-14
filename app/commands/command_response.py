from typing import Any, Literal

from pydantic import BaseModel, Field


class CommandResponse(BaseModel):
    """Структура ответа команды."""

    status: Literal["success", "error", "pending"] = Field(
        ..., description="Статус выполнения команды"
    )

    data: dict | None = Field(None, description="Дополнительные данные")

    error: str | None = Field(None, description="Сообщение об ошибке")

    redirect: str | None = Field(None, description="Команда для перенаправления")
    redirect_data: dict[str, Any] | None = Field(
        None, description="Данные для перенаправления"
    )

    class Config:
        # Позволяет использовать дефолтные значения
        use_enum_values = True

    @classmethod
    def _ok(cls, data: dict | None = None) -> "CommandResponse":
        """✅ Успешный ответ."""
        return cls(
            status="success",
            data=data or {},
            error=None,
            redirect=None,
            redirect_data=None,
        )

    @classmethod
    def _err(cls, error: str, data: dict | None = None) -> "CommandResponse":
        """❌ Ответ с ошибкой."""
        return cls(
            status="error",
            error=error,
            data=data or {},
            redirect=None,
            redirect_data=None,
        )

    @classmethod
    def _pending(cls, data: dict | None = None) -> "CommandResponse":
        """⏳ Ответ в ожидании."""
        return cls(
            status="pending",
            data=data or {},
            error=None,
            redirect=None,
            redirect_data=None,
        )

    @classmethod
    def _redirect(cls, command: str, data: dict | None = None) -> "CommandResponse":
        """🔄 Перенаправление на другую команду."""
        return cls(
            status="success",
            redirect=command,
            redirect_data=data or {},
            data=data or {},
            error=None,
        )

    def is_ok(self) -> bool:
        """Успешный ответ?"""
        return self.status == "success" and not self.redirect

    def is_error(self) -> bool:
        """Ответ с ошибкой?"""
        return self.status == "error"

    def is_pending(self) -> bool:
        """Ответ в ожидании?"""
        return self.status == "pending"

    def is_redirect(self) -> bool:
        """Требуется перенаправление?"""
        return bool(self.redirect)
