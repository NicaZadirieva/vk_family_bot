from app.commands.base import ICommand


class AddBirthdayEventCmd(ICommand):
    """
    Добавление: имя, дата, напоминание за N дней (по умолчанию за 1 день и в день события утром).
    Доступно как родителю, так и ребёнку
    """
