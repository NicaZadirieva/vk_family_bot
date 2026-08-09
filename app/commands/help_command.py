from typing import Any

from app.commands.base.base_command import Command, CommandResult


class HelpCommand(Command):
    """Команда с Fluent API для настройки справки."""

    def __init__(self):
        super().__init__()
        self._command_name: str | None = None
        self._description: str | None = None
        self._usage: str | None = None
        self._examples: list[str] = []
        self._args: dict[str, str] = {}
        self._next_command: Command | None = None

    def for_command(self, name: str) -> "HelpCommand":
        """Устанавливает команду, для которой показывается справка."""
        self._command_name = name
        return self

    def with_description(self, description: str) -> "HelpCommand":
        """Устанавливает описание команды."""
        self._description = description
        return self

    def with_usage(self, usage: str) -> "HelpCommand":
        """Устанавливает пример использования."""
        self._usage = usage
        return self

    def with_example(self, example: str) -> "HelpCommand":
        """Добавляет пример использования."""
        self._examples.append(example)
        return self

    def with_arg(self, name: str, description: str) -> "HelpCommand":
        """Добавляет аргумент команды."""
        self._args[name] = description
        return self

    def then(self, command: Command) -> "HelpCommand":
        """Устанавливает команду для выполнения после справки."""
        self._next_command = command
        return self

    async def execute(self, context: dict[str, Any]) -> CommandResult:
        """Показывает справку."""

        # Формируем справку из настроек
        help_data = {
            "command": self._command_name,
            "description": self._description or "No description",
            "usage": self._usage or "No usage info",
            "examples": self._examples,
            "args": self._args,
        }

        # Выводим справку
        self._print_help(help_data)

        # Передаем управление дальше
        return CommandResult(
            success=True, data=help_data, next_command=self._next_command
        )

    # TODO: переделать под передачу в VK
    def _print_help(self, help_data: dict):
        """Выводит отформатированную справку."""
        print("\n" + "═" * 60)
        print(f"  📖  {help_data['command'].upper()}")
        print("═" * 60)
        print(f"  {help_data['description']}")

        if help_data["usage"]:
            print(f"\n  ► Usage: {help_data['usage']}")

        if help_data["examples"]:
            print("\n  ► Examples:")
            for ex in help_data["examples"]:
                print(f"    • {ex}")

        if help_data["args"]:
            print("\n  ► Arguments:")
            for arg, desc in help_data["args"].items():
                print(f"    • {arg}: {desc}")

        print("═" * 60 + "\n")
