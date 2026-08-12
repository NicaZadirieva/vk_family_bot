from app.commands.base import ICommand


class MyPointsCmd(ICommand):
    """
    Кнопка “⭐ Мои баллы” или команда “/my_points” → бот показывает текущий баланс и последние 5 операций.
    """
