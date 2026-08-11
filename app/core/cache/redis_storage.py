from app.core.cache.storage_interface import ICacheStorage


class RedisCacheStorage(ICacheStorage):
    """Реализация для Redis."""

    def __init__(self, redis_client):
        self._redis = redis_client

    async def get(self, key: str) -> str | None:
        return await self._redis.get(key)
