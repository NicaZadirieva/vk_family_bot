from app.commands.base import ICommand


class ReadCommonNotesCmd(ICommand):
    """
    Ребёнок может читать только общие семейные заметки (без права редактирования).
    """
