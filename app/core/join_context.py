from dataclasses import dataclass


@dataclass
class JoinContext:
    """
    Вспомогательный объект для присоединения (/join) к чату семьи
    """

    password: str
    user_id: int
    family_id: int
    vk_id: int
