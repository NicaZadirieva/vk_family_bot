from app.exceptions.database_error import DatabaseError


class NotFoundError(DatabaseError):
    """Объект не найден."""

    def __init__(
        self,
        entity: str = "Объект",
        identifier: str | None = None,
        message: str | None = None,
        code: str = "NOT_FOUND",
    ):
        self.entity = entity
        self.identifier = identifier

        if message is None:
            if identifier:
                message = f"{entity} с идентификатором '{identifier}' не найден"
            else:
                message = f"{entity} не найден"

        super().__init__(
            message=message,
            code=code,
            details={"entity": entity, "identifier": identifier},
            user_message=message,
        )
