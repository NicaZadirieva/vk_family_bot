import logging
from typing import Any

from app.commands.base import ICommand
from app.core.services.family import FamilyService
from app.handlers.user_info import UserInfo
from app.presenter import Presenter

logger = logging.getLogger(__name__)


class CreateFamilyCmd(ICommand):
    # Класс-хранилище состояний
    _user_states: dict[str, str] = {}

    def __init__(
        self,
        presenter: Presenter,
        user_info: UserInfo,
        family_name: str = "",
        family_service: FamilyService | None = None,
    ):
        super().__init__(presenter)
        self.user_info = user_info
        self.family_name = family_name
        self._family_service = family_service

    async def _set_user_state(self, vk_id: str, state: str) -> None:
        """Сохраняет состояние в памяти."""
        self._user_states[vk_id] = state

    async def _clear_user_state(self, vk_id: str) -> None:
        """Очищает состояние в памяти."""
        if vk_id in self._user_states:
            del self._user_states[vk_id]

    async def _get_user_state(self, vk_id: str) -> str | None:
        """Получает состояние из памяти."""
        return self._user_states.get(vk_id)

    async def execute(self) -> Any:
        # Проверяем, не ждёт ли пользователь подтверждения
        current_state = await self._get_user_state(self.user_info.vk_id)  # type: ignore

        if current_state == "waiting_family_name":
            # Если пользователь уже в процессе, используем введённое имя
            if self.family_name:
                return await self._create_family()
            else:
                await self.presenter.show_only_text(
                    vk_id=self.user_info.vk_id,
                    text="Пожалуйста, введите название семьи",
                )
                return

        if not self.family_name:
            # Запрашиваем имя семьи
            await self._set_user_state(self.user_info.vk_id, "waiting_family_name")  # type: ignore
            await self.presenter.show_only_text(
                vk_id=self.user_info.vk_id,
                text="Введите уникальное название для Вашей семьи",
            )
            return

        # Если имя передано сразу
        return await self._create_family()

    async def _create_family(self) -> None:
        """Создаёт семью с полученным именем."""
        try:
            if not self._family_service:
                raise ValueError("FamilyService не инициализирован")

            # Проверяем, не занято ли имя
            # existing_family = await self._family_service.get_family_by_name(
            #    self.family_name
            # )
            # if existing_family:
            #    await self.presenter.show_only_text(
            #        vk_id=self.user_info.vk_id,
            #        text=f"❌ Семья с именем '{self.family_name}' уже существует. Пожалуйста, выберите другое имя.",
            #    )
            #    return

            await self._family_service.create(
                name=self.family_name,
                link=self.user_info.link,  # type: ignore
            )

            await self.presenter.show_only_text(
                vk_id=self.user_info.vk_id,
                text=f"✅ Семья '{self.family_name}' успешно создана!",
            )

            # Очищаем состояние
            await self._clear_user_state(self.user_info.vk_id)  # type: ignore

        except ValueError as e:
            await self.presenter.show_only_text(
                vk_id=self.user_info.vk_id,
                text=f"❌ {str(e)}",  # noqa: RUF010
            )
        except Exception as e:
            logger.error(f"Ошибка при создании семьи: {e}")
            await self.presenter.show_only_text(
                vk_id=self.user_info.vk_id,
                text="❌ Произошла ошибка при создании семьи. Попробуйте позже.",
            )
