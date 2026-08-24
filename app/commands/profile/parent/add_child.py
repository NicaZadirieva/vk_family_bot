from app.commands.base import ICommand
from app.core.di.services_container import ServicesContainer
from app.core.repositories.base_user_state_repo import UserState


class AddChildCmd(ICommand):
    """
    Приглашение других детей происходит по команде /add_child @ИмяВК Имя_профиля.
    Бот проверяет, что этот VK ID не состоит в другой семье и что пользователь с таким VK_ID существует в VK,
    если это так, генерирует 6-значный код.
    При ошибке проверки — отказывать в генерации кода с сообщением о технической проблеме.
    """

    def __init__(self, services: ServicesContainer):
        self.services = services

    @property
    def name(self) -> str:
        return "add_child"
    
    
    def execute(self, user_id: int, state: UserState, payload: dict | None = None)-> tuple[str, str]:


        
