from typing import Optional
from app.commands.base.base_command import Command


class SceneResult:
    """Результат обработки"""

    def __init__(self, completed: bool, message: str, next_command: Command | None):
        self.completed = completed
        self.message = message
        self.next_command = next_command
