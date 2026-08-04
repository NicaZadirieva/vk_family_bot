from app.database.services.user_service import UserService


class StartCommand():
	# TODO: возможно придется отрефакторить под паттерн строитель/фабрика
	def __init__(self, service: UserService, user_id: int, family_id: int):
		# Поиск user_id в БД и текущей семье
		# Если True, в команде Start не делаем ничего
		# Если False, пишет "Вы не состоите в семье. Пожалуйста, войдите через секретный пароль"
		# показывает кнопку "Войти по паролю" (команда /join)
		