from app.commands.base import ICommand


class ReadNoteCmd(ICommand):
    """
    Просмотр: команда “/read_note” → список заголовков → выбор → полный текст.
    """
