from app.core.repositories.note import NoteRepo


class NoteService:
    """Работа над сущностью Заметка"""

    def __init__(self, repo: NoteRepo):
        self._repo = repo
