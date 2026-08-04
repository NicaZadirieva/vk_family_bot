from app.errors.domain_error import DomainError


class LackOfDataError(DomainError):
    def __init__(self, required_data: str, passed_data: dict):
        super().__init__(
            message=f"Required data: {required_data}, passed: {passed_data}",
            details={"required_data": required_data, "passed_data": passed_data},
        )
