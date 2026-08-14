import asyncio
import logging

from app.command_handler import CmdHandler
from app.presenter import Presenter
from app.scheduler import Scheduler
from app.vk_api.vk_client import VKClient

logger = logging.getLogger(__name__)


class Bot:
    """Основной класс бота"""

    def __init__(self, client: VKClient, presenter: Presenter, scheduler: Scheduler):
        self.client = client
        self.presenter = presenter
        self.scheduler = scheduler
        self.handler = CmdHandler(presenter)
        self._running = False

    def start(self) -> None:
        """Запуск бота (синхронный метод)"""
        try:
            asyncio.run(self._start_async())
        except KeyboardInterrupt:
            logger.info("Бот остановлен пользователем")
            self.stop()
        except Exception as e:
            logger.critical(f"Ошибка при запуске бота: {e}", exc_info=True)
            raise

    def stop(self) -> None:
        """Остановка бота"""
        self._running = False
        logger.info("Бот останавливается...")

    async def _start_async(self) -> None:
        """Асинхронный запуск"""
        self._running = True
        logger.info("VK бот запускается...")
        await self.scheduler.start()

        try:
            lp_data = await self.client.get_longpoll_server()
            server = lp_data.get("server")
            if not server:
                raise RuntimeError("LongPoll server not found")

            key = lp_data["key"]
            ts = lp_data["ts"]
            logger.info(f"LongPoll подключён. server={server}")

            while self._running:
                events = await self.client.poll_events(server, key, ts)

                if "failed" in events:
                    if events.get("failed") == 1:
                        ts = events.get("ts", ts)
                    else:
                        lp_data = await self.client.get_longpoll_server()
                        server = lp_data["server"]
                        key = lp_data["key"]
                        ts = lp_data["ts"]
                    continue

                ts = events["ts"]
                for update in events.get("updates", []):
                    command = await self.handler._handle_update(update)
                    if command:
                        await command.execute()

        except asyncio.CancelledError:
            logger.info("LongPoll цикл отменён")
        except Exception as e:
            logger.critical(f"Ошибка в longpoll: {e}", exc_info=True)
        finally:
            await self.scheduler.shutdown()
            await self.client.close()
            logger.info("VK бот остановлен")
