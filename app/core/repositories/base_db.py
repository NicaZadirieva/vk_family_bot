import logging

from sqlalchemy.exc import (
    InterfaceError,
    InvalidRequestError,
    OperationalError,
    ResourceClosedError,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.database_error import DatabaseError

logger = logging.getLogger(__name__)


class BaseDbRepo:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def _safe_rollback(self) -> None:
        """
        Безопасный rollback с обработкой всех возможных ошибок.
        """
        try:
            await self.db_session.rollback()
            logger.debug("✅ Rollback выполнен успешно")
        except ResourceClosedError as e:
            # Сессия уже закрыта
            logger.warning(f"⚠️ ResourceClosedError при rollback: {e}")
            # Пропускаем, так как сессия уже закрыта
        except InvalidRequestError as e:
            # Сессия уже закрыта или транзакция не активна
            logger.warning(f"⚠️ InvalidRequestError при rollback: {e}")
            # В этом случае ничего не делаем, сессия уже в корректном состоянии

        except OperationalError as e:
            # Проблемы с подключением к БД
            logger.error(f"❌ OperationalError при rollback: {e}")
            # Пробуем восстановить соединение или создаем новую сессию
            await self._handle_connection_error(e)

        except InterfaceError as e:
            # Ошибка интерфейса БД (например, потеря соединения)
            logger.error(f"❌ InterfaceError при rollback: {e}")
            await self._handle_connection_error(e)

        except SQLAlchemyError as e:
            # Любая другая ошибка SQLAlchemy
            logger.error(f"❌ SQLAlchemyError при rollback: {e}")
            # Пробуем принудительно закрыть сессию
            await self._force_close_session()

        except Exception as e:
            # Неожиданная ошибка
            logger.error(f"❌ Неожиданная ошибка при rollback: {e}", exc_info=True)
            # Пробуем принудительно закрыть сессию
            await self._force_close_session()

    async def _handle_connection_error(self, error: Exception) -> None:
        """
        Обработка ошибок соединения с БД.
        """
        try:
            # Пробуем переподключиться
            await self.db_session.close()
            # Создаем новое соединение (если есть механизм)
            # await self.db_session.bind.connect()
            logger.info("🔄 Попытка восстановления соединения с БД")

        except Exception as e:
            logger.error(f"❌ Не удалось восстановить соединение: {e}")
            raise DatabaseError(
                message="Потеря соединения с базой данных",
                details={"original_error": str(error)},
            )

    async def _force_close_session(self) -> None:
        """
        Принудительное закрытие сессии.
        """
        try:
            await self.db_session.close()
            logger.info("🔒 Сессия принудительно закрыта")
        except Exception as e:
            logger.error(f"❌ Ошибка при закрытии сессии: {e}")
