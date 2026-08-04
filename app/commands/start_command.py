from app.services.login_service import LoginService


class StartCommand:
    # TODO: возможно придется отрефакторить под паттерн строитель/фабрика
    def __init__(self, login_service: LoginService):
        self._login_service = login_service

    async def exec(self, vk_id: int, family_id: int):
        # Поиск user_id в БД и текущей семье
        # Если True, в команде Start не делаем ничего
        # Если False, пишет "Вы не состоите в семье. Пожалуйста, войдите через секретный пароль"
        # показывает кнопку "Войти по паролю" (команда /join)
        is_user_allowed = await self._login_service.is_user_allowed(vk_id, family_id)
