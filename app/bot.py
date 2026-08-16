import asyncio
import logging
import sys

from app.handlers.command_handler import CmdHandler
from app.presenter import Presenter
from app.scheduler import Scheduler
from app.vk_api.vk_client import VKClient

logger = logging.getLogger(__name__)


class Bot:
    """Основной класс бота"""

    def __init__(
        self,
        vk_client: VKClient,
        presenter: Presenter,
        scheduler: Scheduler,
        cmd_handler: CmdHandler,
    ):
        self.client = vk_client
        self.presenter = presenter
        self.scheduler = scheduler
        self.handler = cmd_handler
        self._running = False

    def stop(self) -> None:
        """Остановка бота"""
        self._running = False
        logger.info("Бот останавливается...")

    async def start(self):
        """Запуск бота"""
        self._running = True
        logger.info("🚀 Бот запущен")

        try:
            # Проверяем настройки LongPoll
            settings = await self.client.check_longpoll_settings()
            logger.info(f"📋 Настройки LongPoll: {settings}")

            # Получаем данные для LongPoll
            self._longpoll_data = await self.client.get_longpoll_server()
            logger.info(
                f"✅ LongPoll данные получены: {self._longpoll_data.get('key')}"
            )
        except Exception as e:
            logger.error(f"❌ Ошибка получения LongPoll данных: {e}")
            raise

        # Запускаем планировщик
        asyncio.create_task(self.scheduler.start())

        # Запускаем обработку сообщений
        self._task = asyncio.create_task(self._poll_messages())

        try:
            await self._task
        except asyncio.CancelledError:
            logger.info("Задача обработки сообщений отменена")
            raise

    async def _poll_messages(self):
        """Основной цикл опроса LongPoll"""
        logger.info("🔄 Начинаем опрос LongPoll...")
        print("🔄 === НАЧАЛО ОПРОСА LONGPOLL ===")
        sys.stdout.flush()

        ts = self._longpoll_data.get("ts")
        key = self._longpoll_data.get("key")
        server = self._longpoll_data.get("server")

        if not all([ts, key, server]):
            logger.error("❌ Неполные данные LongPoll")
            return

        while self._running:
            try:
                print(f"🔄 === ЦИКЛ ОПРОСА, _running={self._running} ===")
                sys.stdout.flush()

                # Опрашиваем LongPoll сервер
                data = await self.client.poll_events(server, key, ts, wait=25)  # type: ignore

                print(f"📦 === ПОЛУЧЕНЫ ДАННЫЕ: {data.get('updates', [])} ===")
                sys.stdout.flush()

                # Проверяем ошибки
                if "failed" in data:
                    failed_code = data["failed"]
                    logger.warning(f"⚠️ LongPoll ошибка: {failed_code}")

                    if failed_code == 1:
                        # История устарела, просто обновляем ts
                        ts = data.get("ts", ts)
                        logger.info(f"🔄 Обновлен ts: {ts}")
                        continue
                    elif failed_code == 2:
                        # Ключ истек, получаем новый
                        logger.info("🔄 Ключ истек, получаем новый...")
                        longpoll_data = await self.client.get_longpoll_server()
                        key = longpoll_data.get("key")
                        server = longpoll_data.get("server")
                        ts = longpoll_data.get("ts")
                        continue
                    elif failed_code == 3:
                        # Информация потеряна, получаем новую
                        logger.info("🔄 Информация потеряна, получаем новую...")
                        longpoll_data = await self.client.get_longpoll_server()
                        key = longpoll_data.get("key")
                        server = longpoll_data.get("server")
                        ts = longpoll_data.get("ts")
                        continue
                    else:
                        logger.error(f"❌ Неизвестная ошибка LongPoll: {failed_code}")
                        await asyncio.sleep(1)
                        continue

                # Обновляем ts
                ts = data.get("ts", ts)

                # Обрабатываем обновления
                updates = data.get("updates", [])
                if updates:
                    print(f"📨 === ПОЛУЧЕНО {len(updates)} ОБНОВЛЕНИЙ ===")
                    sys.stdout.flush()

                    for update in updates:
                        print(f"📨 === ОБНОВЛЕНИЕ: {update} ===")
                        sys.stdout.flush()
                        await self.handler._handle_update(update)

                # Небольшая пауза, чтобы не нагружать сервер
                await asyncio.sleep(0.1)

            except asyncio.CancelledError:
                logger.info("Опрос LongPoll остановлен")
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле LongPoll: {e}", exc_info=True)
                await asyncio.sleep(1)
