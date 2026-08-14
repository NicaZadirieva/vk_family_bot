from abc import ABC
from typing import Any


class ICommand(ABC):
    def __init__(self, presenter):
        self.presenter = presenter

    def execute(self) -> Any: ...
    def undo(self) -> Any: ...
