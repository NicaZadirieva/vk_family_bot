from app.errors.domain_error import DomainError


class NotFoundError(DomainError):
    def __init__(self, reason: str, passed_data: dict):
        super().__init__(
            message=f"Данные не найдены. {reason}",
            details={"passed_data": passed_data},
        )
