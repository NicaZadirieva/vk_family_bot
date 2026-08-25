from app.core.di.services_container import ServicesContainer
from app.states.add.add_child_user_profile import AddChildUserProfileState
from app.states.add.add_child_vk_name import AddChildVkNameState
from app.states.add.generate_child_password import GenerateChildPasswordState
from .base import IState
from .main_state import MainState


# Фабрика состояний
_state_registry = {
    "main": MainState,
    "generate_child_password": GenerateChildPasswordState,
    "add_child_user_profile": AddChildUserProfileState,
    "add_child_vk_name": AddChildVkNameState,
}


def get_state(
    state_name: str, services: ServicesContainer | None = None
) -> IState | None:
    """
    Возвращает экземпляр состояния по имени.

    Args:
        state_name: Имя состояния
        service: Сервис для работы с данными (обязателен для некоторых состояний)

    Returns:
        IState: Экземпляр состояния или None
    """
    state_class = _state_registry.get(state_name)
    if not state_class:
        return None

    # Проверяем, нужен ли service для этого состояния
    import inspect

    sig = inspect.signature(state_class.__init__)

    # Если конструктор требует services и он передан
    if "services" in sig.parameters:
        if services is None:
            raise ValueError(f"State {state_name} requires service parameter")
        return state_class(services)

    # Если конструктор не требует service
    return state_class()


__all__ = [
    "IState",
    "MainState",
    "get_state",
]
