from app.core.repositories.task import TaskRepo


class TaskService:
    """Работа над сущностью Задача"""

    def __init__(self, repository: TaskRepo):
        self._repo = repository
