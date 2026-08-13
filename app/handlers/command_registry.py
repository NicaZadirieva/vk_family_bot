import logging
from typing import Callable  # noqa: UP035

logger = logging.getLogger(__name__)


class CommandRegistry:
    """
    Простой реестр команд с поддержкой алиасов.
    """

    _commands: dict[str, Callable] = {}
    _aliases: dict[str, str] = {}  # алиас -> основное имя команды

    @classmethod
    def register(cls, handler: Callable, name: str, aliases: list[str] | None = None):
        """
        Регистрация обработчика команды.

        Args:
            handler: Асинхронная функция-обработчик
            name: Основное имя команды
            aliases: Список алиасов (дополнительных имен)

        Example:
            CommandRegistry.register(handle_start, "start", ["старт", "привет"])
        """
        # Регистрируем основную команду
        cls._commands[name] = handler
        logger.debug(f"Зарегистрирована команда: {name}")

        # Регистрируем алиасы
        if aliases:
            for alias in aliases:
                cls._aliases[alias] = name
                logger.debug(f"Алиас '{alias}' -> '{name}'")

    @classmethod
    def get_handler(cls, command: str) -> Callable | None:
        """
        Получение обработчика по имени команды или алиасу.

        Returns:
            Callable или None, если команда не найдена
        """
        # Сначала ищем прямую команду
        if command in cls._commands:
            return cls._commands[command]

        # Затем ищем алиас
        if command in cls._aliases:
            main_command = cls._aliases[command]
            return cls._commands.get(main_command)

        return None

    @classmethod
    def get_all_commands(cls) -> list[str]:
        """Получить список всех зарегистрированных команд."""
        return list(cls._commands.keys())

    @classmethod
    def clear(cls):
        """Очистка реестра (для тестов)."""
        cls._commands.clear()
        cls._aliases.clear()
