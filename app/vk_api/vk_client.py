import asyncio
import json
import logging
import random
import ssl
import time
from typing import Any, Dict, Optional  # noqa: UP035

import aiohttp
from aiohttp import ClientSession, ClientTimeout, TCPConnector

from app.settings import settings

logger = logging.getLogger(__name__)


class VKClient:
    def __init__(self, token: str, version: str = "5.199"):
        self.token = token
        self.version = version
        self.api_url = "https://api.vk.com/method/"
        self.session: ClientSession | None = None
        self._timeout = ClientTimeout(total=30)

        # SSL контекст с отключенной проверкой
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        self._connector = TCPConnector(ssl=ssl_context)

    async def _ensure_session(self) -> ClientSession:
        """Создает или возвращает существующую сессию"""
        if self.session is None or self.session.closed:
            logger.debug("🔄 Создание новой сессии")
            self.session = ClientSession(
                timeout=self._timeout, connector=self._connector
            )
        return self.session

    async def _request(self, method: str, params: dict):
        """Выполнение запроса к VK API с полной проверкой"""
        try:
            # Убеждаемся, что сессия создана
            session = await self._ensure_session()

            params["access_token"] = self.token
            params["v"] = self.version

            if method == "messages.send" and "random_id" not in params:
                params["random_id"] = random.randint(1, 10**9)

            url = f"https://api.vk.com/method/{method}"

            logger.debug(f"📤 Запрос к VK API: {method}, params: {params}")

            async with session.post(url, data=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"HTTP {response.status}: {error_text}")
                    raise Exception(f"HTTP error: {response.status}")

                data = await response.json()

                if not data:
                    logger.error("Empty response from VK API")
                    raise Exception("Empty response from VK API")

                if "error" in data:
                    error = data["error"]
                    error_code = error.get("error_code")
                    error_msg = error.get("error_msg", "unknown")
                    logger.error(f"VK API error {error_code}: {error_msg}")
                    raise Exception(f"VK API error {error_code}: {error_msg}")

                # Получаем ответ
                result = data.get("response")

                # Проверяем, что ответ не None
                if result is None:
                    logger.warning(f"⚠️ VK API вернул None для метода {method}")
                    # Для некоторых методов это нормально (например, messages.send возвращает None в случае ошибки)
                    return None

                logger.debug(f"✅ VK API ответ: {result}")
                return result

        except Exception as e:
            logger.error(f"❌ Ошибка в _request: {e}", exc_info=True)
            raise

    def _generate_random_id(self) -> int:
        return int(time.time() * 1000) + random.randint(0, 1000)

    async def send_message(
        self, user_id: int, message: str, keyboard: Dict | None = None
    ):
        """Отправка сообщения пользователю"""
        try:
            logger.info(f"📤 Отправка сообщения пользователю {user_id}")
            logger.debug(f"Сообщение: {message[:100]}...")

            params = {
                "user_id": user_id,
                "message": message,
                "random_id": random.randint(1, 2**31),
                "v": self.version,
            }

            if keyboard:
                # Убеждаемся, что клавиатура в правильном формате
                if isinstance(keyboard, dict):
                    params["keyboard"] = json.dumps(keyboard, ensure_ascii=False)
                elif isinstance(keyboard, str):
                    params["keyboard"] = keyboard
                else:
                    logger.warning(f"⚠️ Неверный формат клавиатуры: {type(keyboard)}")

                logger.debug(f"📤 Отправка клавиатуры: {params['keyboard'][:200]}...")

            response = await self._request("messages.send", params)

            # Проверяем ответ
            if response is None:
                logger.warning(f"⚠️ VK вернул None при отправке сообщения {user_id}")
                # Возвращаем 0 как признак успеха, но без ID сообщения
                return 0

            logger.info(
                f"✅ Сообщение отправлено пользователю {user_id}, ID: {response}"
            )
            return response

        except Exception as e:
            logger.error(f"❌ Ошибка при отправке сообщения: {e}", exc_info=True)
            raise

    async def get_longpoll_server(self) -> Dict[str, Any]:
        """Получение данных для LongPoll подключения"""
        try:
            logger.info("🔄 Запрос LongPoll сервера...")
            result = await self._request(
                "groups.getLongPollServer",
                {"group_id": settings.vk_app.VK_GROUP_ID},
            )

            if result is None:
                logger.error("❌ LongPoll сервер вернул None")
                raise Exception("LongPoll server returned None")

            logger.info("✅ LongPoll сервер получен")
            logger.debug(f"LongPoll server response: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ Ошибка получения LongPoll сервера: {e}")
            raise

    async def poll_events(
        self, server: str, key: str, ts: int, wait: int = 25
    ) -> Dict[str, Any]:
        """Опрос LongPoll сервера для получения событий"""
        if not server:
            logger.error("❌ LongPoll server is empty")
            raise ValueError("LongPoll server is empty")

        try:
            session = await self._ensure_session()

            # Пробуем разные режимы: mode=2 для сообщений, mode=234 для всех событий
            url = f"{server}?act=a_check&key={key}&ts={ts}&wait={wait}&mode=234"
            logger.info(f"🔄 LongPoll запрос")
            logger.debug(f"URL: {url.replace(key, 'HIDDEN')}")

            async with session.get(url, timeout=30) as resp:
                logger.info(f"📊 LongPoll статус: {resp.status}")

                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(
                        f"❌ LongPoll ошибка: статус {resp.status}, текст: {error_text}"
                    )
                    return {"failed": 2}

                data = await resp.json()

                # Логируем ВЕСЬ ответ полностью
                logger.info(
                    f"📦 LongPoll ОТВЕТ (полный): {json.dumps(data, ensure_ascii=False, default=str)}"
                )

                # Проверяем наличие ключей
                logger.info(f"🔑 Ключи в ответе: {list(data.keys())}")

                # Проверяем ts
                new_ts = data.get("ts")
                if new_ts:
                    logger.info(f"🕐 Новый ts: {new_ts} (старый: {ts})")

                # Проверяем failed
                if "failed" in data:
                    logger.warning(f"⚠️ LongPoll failed: {data['failed']}")
                    return data

                # Проверяем updates
                updates = data.get("updates", [])
                logger.info(f"📨 Количество обновлений: {len(updates)}")

                if len(updates) > 0:
                    logger.info(
                        f"📨 ТИПЫ обновлений: {[u.get('type') for u in updates]}"
                    )
                    # Логируем первое обновление полностью
                    logger.info(
                        f"📨 Первое обновление: {json.dumps(updates[0], ensure_ascii=False, default=str)}"
                    )
                else:
                    # Если нет обновлений, проверяем, может быть они в другом поле
                    for key in data.keys():
                        if key not in ["ts", "failed", "updates"]:
                            logger.info(f"🔍 Дополнительное поле '{key}': {data[key]}")

                return data

        except asyncio.TimeoutError:
            logger.error("⏰ LongPoll таймаут")
            return {"failed": 2}
        except aiohttp.ClientError as e:
            logger.error(f"🌐 LongPoll клиентская ошибка: {e}")
            return {"failed": 2}
        except Exception as e:
            logger.error(f"❌ LongPoll неизвестная ошибка: {e}", exc_info=True)
            return {"failed": 2}

    async def check_longpoll_settings(self) -> Dict[str, Any]:
        """Проверка настроек LongPoll для группы"""
        try:
            logger.info("🔄 Проверка настроек LongPoll...")
            result = await self._request(
                "groups.getLongPollSettings",
                {"group_id": settings.vk_app.VK_GROUP_ID},
            )
            logger.info(
                f"✅ Настройки LongPoll: {json.dumps(result, ensure_ascii=False, default=str)}"
            )
            return result
        except Exception as e:
            logger.error(f"❌ Ошибка получения настроек LongPoll: {e}")
            raise

    async def answer_message_event(self, event_id: str, user_id: int, peer_id: int):
        """Ответ на событие от inline кнопки (обязательно для VK)"""
        try:
            logger.info(f"🔄 Ответ на событие: event_id={event_id}, user_id={user_id}")
            params = {
                "event_id": event_id,
                "user_id": user_id,
                "peer_id": peer_id,
            }
            result = await self._request("messages.sendMessageEventAnswer", params)

            if result is None:
                logger.warning(f"⚠️ Ответ на событие вернул None")
                return None

            logger.info("✅ Ответ на событие отправлен")
            return result
        except Exception as e:
            logger.error(f"❌ Ошибка при ответе на событие: {e}")
            raise

    async def close(self):
        """Закрытие сессии"""
        try:
            if self.session:
                logger.info("🔄 Закрытие сессии VK Client...")
                await self.session.close()
                logger.info("✅ Сессия VK Client закрыта")
        except Exception as e:
            logger.error(f"❌ Ошибка при закрытии сессии: {e}")
