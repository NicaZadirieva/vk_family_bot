import asyncio
import logging

from app.bot import Bot
from app.core.db.session import async_session
from app.utils.logs_util import LoggerUtils

logger = logging.getLogger(__name__)


async def main():
    """Главная функция"""
    LoggerUtils.setup_logger()
    async with async_session() as session:
        # репозитории, сервисы, сессия session (DI зависимости)
        bot = Bot()

        try:
            await bot.start()
        except KeyboardInterrupt:
            await bot.stop()
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            await bot.stop()
            raise


if __name__ == "__main__":
    asyncio.run(main())
