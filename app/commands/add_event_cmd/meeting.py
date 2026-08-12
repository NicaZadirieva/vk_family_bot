from app.commands.base import ICommand


class AddMeetingEventCmd(ICommand):
    """
    Родитель добавляет разовую встречу:
    название,
    дата,
    время,
    настраиваемое напоминание.
    """
