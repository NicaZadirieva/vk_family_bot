import asyncio
import json
import logging

from app.core.di.services_container import ServicesContainer
from app.handlers.message_handler import MessageHandler
from app.settings import settings
from app.vk_api.vk_client import VKClient

logger = logging.getLogger(__name__)


class Bot:
    """Основной класс бота"""

    def __init__(self, services: ServicesContainer):
        self.vk_client = VKClient(
            token=settings.vk_app.VK_API_TOKEN,  # type: ignore
        )
        self.message_handler = MessageHandler(self.vk_client, services)
        self.services = services
        self.is_running = False

    async def start(self):
        """Запуск бота"""
        try:
            logger.info("🚀 Запуск бота...")
            self.is_running = True
            await self._listen_messages()
        except Exception as e:
            logger.error(f"❌ Ошибка при запуске бота: {e}")
            raise

    async def _listen_messages(self):
        """Прослушивание входящих сообщений через LongPoll"""
        logger.info("👂 Бот начал прослушивание сообщений...")
        try:
            lp_data = await self.vk_client.get_longpoll_server()
            server = lp_data.get("server")
            if not server:
                logger.error(f"Invalid LongPoll response: {lp_data}")
                raise RuntimeError("LongPoll server not found")

            key = lp_data["key"]
            ts = lp_data["ts"]
            logger.info(f"✅ LongPoll подключен. server={server}, key={key}, ts={ts}")

            while self.is_running:
                events = await self.vk_client.poll_events(server, key, ts)

                if "failed" in events:
                    if events.get("failed") == 1:
                        ts = events.get("ts", ts)
                        logger.info(f"LongPoll: обновлен ts={ts}")
                    else:
                        logger.info("LongPoll: переподключение...")
                        lp_data = await self.vk_client.get_longpoll_server()
                        server = lp_data["server"]
                        key = lp_data["key"]
                        ts = lp_data["ts"]
                    continue

                ts = events["ts"]
                for update in events.get("updates", []):
                    await self._handle_update(update)

        except asyncio.CancelledError:
            logger.info("LongPoll цикл отменён")
        except Exception as e:
            logger.error(f"❌ Ошибка в LongPoll: {e}", exc_info=True)
            raise

    async def _handle_update(self, update: dict):
        """Обработка одного обновления от VK"""
        try:
            # Логируем ВСЕ обновления для отладки
            logger.info(f"📨 Получено обновление: {update.get('type')}")
            logger.debug(
                f"Полное обновление: {json.dumps(update, ensure_ascii=False, default=str)[:500]}"
            )
            # Проверяем тип события
            event_type = update.get("type")

            # Обработка обычных сообщений
            if event_type == "message_new":
                logger.info("💬 Обработка нового сообщения...")

                obj = update.get("object")
                if not obj:
                    logger.warning("⚠️ Объект сообщения пуст")
                    return

                message = obj.get("message")
                if not message:
                    logger.warning("⚠️ Поле message отсутствует")
                    return

                user_id = message.get("from_id")
                message_text = message.get("text", "")
                payload = message.get("payload")

                # Проверяем, что сообщение от пользователя
                if user_id is None:
                    logger.warning("⚠️ Сообщение без from_id")
                    return

                if user_id < 0:
                    logger.debug(
                        f"ℹ️ Сообщение от группы/сервиса: {user_id}, игнорируем"
                    )
                    return

                logger.info(f"👤 От пользователя: {user_id}")
                logger.info(
                    f"📝 Текст: {message_text[:50] if message_text else '[пусто]'}"
                )
                if payload:
                    logger.debug(f"📦 Payload: {payload}")

                # Если текст пустой, но есть вложения
                if not message_text and not payload:
                    attachments = message.get("attachments", [])
                    if attachments:
                        logger.info(
                            f"💬 Сообщение от {user_id} содержит вложения (без текста)"
                        )
                        # Можно обработать как специальную команду
                        message_text = "/attachment"
                    else:
                        logger.info(f"💬 Пустое сообщение от {user_id}, игнорируем")
                        return

                # Обрабатываем сообщение
                logger.debug("🔄 Начинаем обработку сообщения...")
                await self.message_handler.handle_message(
                    user_id=user_id,
                    message_text=message_text,
                    payload=payload,  # payload передается как строка JSON или None
                )
                logger.debug("✅ Обработка сообщения завершена")

            # Обработка событий от inline кнопок
            elif event_type == "message_event":
                logger.info("🔘 Обработка события от inline кнопки...")
                obj = update.get("object")
                if not obj:
                    logger.warning("⚠️ Объект события пуст")
                    return

                # Для message_event своя структура
                user_id = obj.get("user_id")
                payload = obj.get("payload")
                event_id = obj.get("event_id")

                if user_id is None:
                    logger.warning("⚠️ Событие без user_id")
                    return

                logger.info(f"👤 От пользователя: {user_id}")
                logger.info(f"📦 Payload: {payload}")

                # Обрабатываем как сообщение с payload
                await self.message_handler.handle_message(
                    user_id=user_id,
                    message_text="",  # Нет текста
                    payload=json.dumps(payload)
                    if isinstance(payload, dict)
                    else payload,
                )

                # Подтверждаем получение события (важно для VK)
                logger.debug("🔄 Отправка подтверждения события...")
                await self.vk_client.answer_message_event(
                    event_id=event_id, user_id=user_id, peer_id=obj.get("peer_id")
                )
                logger.debug("✅ Подтверждение события отправлено")
            else:
                logger.debug(f"ℹ️ Игнорируем событие типа: {event_type}")

        except Exception as e:
            logger.error(f"❌ Ошибка при обработке обновления: {e}", exc_info=True)

    async def stop(self):
        """Остановка бота"""
        logger.info("🛑 Остановка бота...")
        self.is_running = False

        await self.vk_client.close()
        logger.info("✅ Бот остановлен")
