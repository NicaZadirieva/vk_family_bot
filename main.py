import asyncio
import logging

from app.bot import Bot
from app.commands.profile.master.create_family import CreateFamilyCmd
from app.core.db.session import async_session  # Изменено с async_session
from app.core.di.services_container import ServicesContainer
from app.handlers.command_registry import CommandRegistry
from app.utils.logs_util import LoggerUtils

logger = logging.getLogger(__name__)


async def main():
    """Главная функция"""
    services_container = ServicesContainer()
    LoggerUtils.setup_logger()
    CommandRegistry.register(CreateFamilyCmd, "create_family", ["создать семью"])

    # Создаем сессию и передаем в контейнер
    async with async_session() as session:
        # Переопределяем сессию в контейнере
        services_container.session.override(session)

        bot = Bot(services_container)

        try:
            await bot.start()
        except KeyboardInterrupt:
            logger.info("Бот остановлен пользователем (Ctrl+C)")
            await bot.stop()
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
            await bot.stop()
            raise


if __name__ == "__main__":
    asyncio.run(main())
