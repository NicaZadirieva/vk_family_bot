import time
from dataclasses import dataclass, field


# TODO: посмотреть нужен ли он в redis реализации
@dataclass
class CacheEntry:
    """Запись в кэше с метаданными."""

    value: str
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None

    @property
    def is_expired(self) -> bool:
        """Проверяет, истекло ли время жизни записи."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    @property
    def ttl_remaining(self) -> int:
        """Возвращает оставшееся время жизни в секундах."""
        if self.expires_at is None:
            return -1
        remaining = self.expires_at - time.time()
        return max(0, int(remaining))
