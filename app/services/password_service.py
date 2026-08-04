from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordService:
    """Сервис для работы с паролями (Domain Service)"""

    @staticmethod
    def hash(plain_password: str) -> str:
        """Хеширует пароль"""
        return pwd_context.hash(plain_password)

    @staticmethod
    def verify(plain_password: str, password_hash: str) -> bool:
        """Проверяет пароль"""
        return pwd_context.verify(plain_password, password_hash)

    @staticmethod
    def needs_rehash(password_hash: str) -> bool:
        """Проверяет, нужно ли обновить хеш"""
        return pwd_context.needs_update(password_hash)
