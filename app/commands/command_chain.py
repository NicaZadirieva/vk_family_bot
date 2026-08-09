from typing import Any

from app.commands.base.base_command import Command


class CommandChain:
    """Выполняет цепочку команд."""

    def __init__(self, first_command: Command):
        self._first = first_command

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        """Запускает цепочку команд"""
        current = self._first
        result = None

        while current:
            result = await current.execute(context)

            if not result.success:
                # Можно прервать или выполнить fallback
                context["error"] = result.error
                break

            # Обновляем контекст данными результата
            if result.data:
                context.update(result.data)

            # Получаем следующую команду
            current = current._get_next(result)

        return context
