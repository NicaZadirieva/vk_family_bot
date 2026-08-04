from dataclasses import dataclass
from typing import Any
from app.commands.base_command import Command
from app.errors.invalid_login_error import InvalidLoginError
from app.errors.lack_of_data_error import LackOfDataError

@dataclass
class JoinContext:
	password: str
	user_id: int
	family_id: int
	vk_id: int

class JoinCommand(Command):
	def __get_data_from_context__(self, context: dict[str, Any]) -> JoinContext:
		vk_id = context.get("vk_id")
		family_id = context.get("family_id")
		user_id = context.get("user_id")
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

