from app.core.repositories.reward import RewardRepo


class RewardService:
    """Работа над сущностью Награда"""

    def __init__(self, repository: RewardRepo):
        self._repo = repository
