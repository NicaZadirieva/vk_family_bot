from app.core.repositories.tasks import TasksRepo


class TaskService:
    """Работа над сущностью Задача"""

    def __init__(self, repo: TasksRepo):
        self._repo = repo
