import asyncio
import logging

from app.bot import Bot
from app.commands.profile.master.create_family import CreateFamilyCmd
from app.core.db.session import async_session
from app.core.repositories.family import FamilyRepo
from app.core.services.family import FamilyService
from app.handlers.command_handler import CmdHandler
from app.handlers.command_registry import CommandRegistry
from app.presenter import Presenter
from app.scheduler import Scheduler
from app.settings import settings
from app.utils.logs_util import LoggerUtils
from app.vk_api.vk_client import VKClient

logger = logging.getLogger(__name__)


async def main():
    """Главная функция"""
    LoggerUtils.setup_logger()
    CommandRegistry.register(CreateFamilyCmd, "create_family", ["создать семью"])

    async with async_session() as session:
        vk_client = VKClient(settings.vk_app.VK_API_TOKEN)  # type: ignore
        presenter = Presenter(vk_client)
        scheduler = Scheduler()

        family_repo = FamilyRepo(session)
        family_service = FamilyService(family_repo)

        cmd_handler = CmdHandler(presenter, family_service)

        bot = Bot(vk_client, presenter, scheduler, cmd_handler)

        try:
            await bot.start()
        except KeyboardInterrupt:
            logger.info("Бот остановлен пользователем (Ctrl+C)")
            bot.stop()
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
            bot.stop()
            raise


if __name__ == "__main__":
    asyncio.run(main())
