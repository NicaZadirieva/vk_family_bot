from typing import Any
from app.commands.base_command import Command, CommandResult
from app.core.join_context import JoinContext
from app.errors.invalid_login_error import InvalidLoginError
from app.errors.lack_of_data_error import LackOfDataError
from app.errors.not_found_user import NotFoundError
from app.services.password_service import PasswordService


class JoinCommand(Command):
	"""
	Вход с паролем
	"""
	def __init__(self, password_service: PasswordService):
		super().__init__()
		self._password_service = password_service

	def __get_data_from_context__(self, context: dict[str, Any]) -> JoinContext:
		vk_id = context.get("vk_id")
		family_id = context.get("family_id")
		user_id = context.get("user_id")
		# TODO: пароль вводит юзер. Надо заменить
		password = context.get("password")
		if not vk_id or not family_id or not user_id or not password:
			raise LackOfDataError("vk_id, family_id, user_id", {"vk_id": vk_id, "family_id": family_id, "user_id": user_id})
		try:
			return JoinContext(password=password, vk_id=int(vk_id), family_id=int(family_id), user_id=int(user_id))
		except:
			raise InvalidLoginError("vk_id, family_id не являются валидными id", {"vk_id": vk_id, "family_id": family_id})
    
	async def execute(self, context: dict[str, Any]):
		try:
			data: JoinContext = self.__get_data_from_context__(context)
			is_verified_user = await self._password_service.verify_user(data)
			if is_verified_user:
				return CommandResult(success=True, next_command=)
			else:
				# непредвиденная ситуация
				return CommandResult(success=False, next_command=)
		except NotFoundError as e:
			return СommandResult(success=False, error=e.message, next_command=)
		except LackOfDataError as e:
			return СommandResult(success=False, error=e.message, next_command=)
		except InvalidLoginError as e:
			return СommandResult(success=False, error=e.message, next_command=)
		except Exception as e:
			# непредвиденная ситуация
				return CommandResult(success=False, next_command=)
		