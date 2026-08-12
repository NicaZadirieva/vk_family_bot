from app.core.repositories.reward import RewardRepo


class RewardService:
    """Работа над сущностью Награда"""

    def __init__(self, repo: RewardRepo):
        self._repo = repo
