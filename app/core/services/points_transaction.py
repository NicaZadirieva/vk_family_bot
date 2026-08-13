from app.core.repositories.points_transaction import PointsTransactionRepo


class PointsTransactionService:
    """Работа над обменом баллами между родитель->ребенок"""

    def __init__(self, repo: PointsTransactionRepo):
        self._repo = repo
