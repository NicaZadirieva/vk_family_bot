import json
import time

from app.core.cache.storage_interface import ICacheStorage


class SessionService:
    def __init__(self, cache_storage: ICacheStorage):
        self._cache_storage = cache_storage


    def get_session_by_user(self, user_id: int):
        

    async def start_new_session(self, user_id: int, ttl: int = 3_600):
        # Очищаем старую сессию
        await self._cache_storage.clear_user_session(user_id)

        # Устанавливаем начальное состояние
        await self._cache_storage.set_user_state(user_id, "start_scene")

        # Сохраняем контекст
        await self._cache_storage.set(
            "context",
            json.dumps({"step": "WELCOME", "started_at": time.time()}),
            ttl=ttl,
            user_id=user_id,
        )
