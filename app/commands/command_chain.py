from typing import Any

from app.commands.base_command import Command


class CommandChain:
    """Выполняет цепочку команд."""

    def __init__(self, first_command: Command):
        self._first = first_command

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        current = self._first

        while current:
            result = current.execute(context)

            if not result.success:
                # Можно прервать или выполнить fallback
                break

            current = current._get_next(result)

        return context
