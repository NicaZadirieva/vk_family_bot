import logging
from typing import Any

from app.commands.base import ICommand
from app.core.services.family import FamilyService
from app.handlers.user_info import UserInfo
from app.presenter import Presenter

logger = logging.getLogger(__name__)


class UserStateManager:
    """Менеджер состояний пользователей."""

    _states: dict[str, str] = {}

    @classmethod
    def set_state(cls, vk_id: str, state: str) -> None:
        cls._states[vk_id] = state

    @classmethod
    def get_state(cls, vk_id: str) -> str | None:
        return cls._states.get(vk_id)

    @classmethod
    def clear_state(cls, vk_id: str) -> None:
        cls._states.pop(vk_id, None)


class CreateFamilyCmd(ICommand):
    def __init__(
        self,
        presenter: Presenter,
        user_info: UserInfo,
        family_service: FamilyService,
        family_name: str = "",
    ):
        super().__init__(presenter)
        self.user_info = user_info
        self.family_name = family_name.strip()
        self._family_service = family_service

    async def execute(self) -> Any:
        vk_id = str(self.user_info.vk_id)
        current_state = UserStateManager.get_state(vk_id)

        # Если пользователь в процессе ввода имени
        if current_state == "waiting_family_name":
            if self.family_name:
                # Если введено имя - создаём семью
                UserStateManager.clear_state(vk_id)
                return await self._create_family()
            else:
                # Если пустое сообщение - повторяем запрос
                await self.presenter.show_only_text(
                    vk_id=self.user_info.vk_id,
                    text="Пожалуйста, введите название семьи (не оставляйте пустым)",
                )
                return

        # Если имя не передано - запрашиваем
        if not self.family_name:
            UserStateManager.set_state(vk_id, "waiting_family_name")
            await self.presenter.show_only_text(
                vk_id=self.user_info.vk_id,
                text="Введите уникальное название для Вашей семьи",
            )
            return

        # Если имя передано сразу - создаём семью
        return await self._create_family()

    async def _create_family(self) -> None:
        """Создаёт семью с полученным именем."""
        vk_id = str(self.user_info.vk_id)

        try:
            if not self._family_service:
                raise ValueError("FamilyService не инициализирован")

            # Создаём семью
            await self._family_service.create(
                name=self.family_name,
                link=self.user_info.link,  # type: ignore
            )

            await self.presenter.show_only_text(
                vk_id=self.user_info.vk_id,
                text=f"✅ Семья '{self.family_name}' успешно создана!",
            )

            # Очищаем состояние
            UserStateManager.clear_state(vk_id)

            # Показываем меню добавления
            await self.presenter.show(
                self.user_info.vk_id,
                text="Нажмите добавить родителя или ребенка",
                screen_type="add",
            )

        except ValueError as e:
            await self.presenter.show_only_text(
                vk_id=self.user_info.vk_id,
                text=f"❌ {str(e)}",
            )
        except Exception as e:
            logger.error(f"Ошибка при создании семьи: {e}")
            await self.presenter.show_only_text(
                vk_id=self.user_info.vk_id,
                text="❌ Произошла ошибка при создании семьи. Попробуйте позже.",
            )
