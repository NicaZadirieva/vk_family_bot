from app.core.repositories.reward_request import RewardRequestRepo


class RewardRequestService:
    """Запрашивает разрешение родителя на покупку награды для ребенка"""

    def __init__(self, repo: RewardRequestRepo):
        self._repo = repo
