from app.errors.domain_error import DomainError


class InvalidLoginError(DomainError):
    def __init__(self, reason: str, passed_data: dict):
        super().__init__(
            message=f"Несанкционированный доступ. {reason}",
            details={"passed_data": passed_data},
        )
