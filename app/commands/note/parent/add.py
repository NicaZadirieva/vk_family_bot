from app.commands.base import ICommand


class AddNoteCmd(ICommand):
    """
            Родитель создаёт заметку: заголовок и текст, может добавить маркированный список покупок.
    Команда: “/add_note Список покупок: хлеб, молоко, яблоки”.

    """
