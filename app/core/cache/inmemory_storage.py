import asyncio
import time
from typing import Any

from app.core.cache.cache_expires import CacheEntry
from app.core.cache.namespace_type import NamespaceType
from app.core.cache.storage_interface import ICacheStorage


class InMemoryCacheStorage(ICacheStorage):
    """
    In-memory реализация кэша с поддержкой пользователей и семей.

    Структура данных:
    {
        "global": {
            "config": CacheEntry("value")
        },
        "user:{user_id}": {
            "state": CacheEntry("value"),
            "context": CacheEntry("{...}"),
            "temp_data": CacheEntry("...")
        },
        "family:{family_id}": {
            "members": CacheEntry("[...]"),
            "settings": CacheEntry("{...}")
        }
    }
    """

    def __init__(self, cleanup_interval: int = 60):
        """
        Args:
            cleanup_interval: Интервал очистки просроченных записей в секундах
        """
        self._data: dict[str, dict[str, CacheEntry]] = {}
        self._cleanup_interval = cleanup_interval
        self._start_cleanup_task()

    def _start_cleanup_task(self):
        """Запускает фоновую задачу очистки."""
        asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self):
        """Фоновый цикл очистки просроченных записей."""
        while True:
            await asyncio.sleep(self._cleanup_interval)
            await self._cleanup_expired()

    async def _cleanup_expired(self):
        """Удаляет все просроченные записи."""
        now = time.time()
        expired_count = 0

        for namespace in list(self._data.keys()):
            namespace_data = self._data[namespace]
            expired_keys = [
                key
                for key, entry in namespace_data.items()
                if entry.expires_at and now > entry.expires_at
            ]

            for key in expired_keys:
                del namespace_data[key]
                expired_count += 1

            # Удаляем пустые пространства имен
            if not namespace_data:
                del self._data[namespace]

        if expired_count > 0:
            print(f"🧹 Cleaned up {expired_count} expired cache entries")

    # ========== Методы для работы с пространствами имен ==========

    def _get_namespace(
        self,
        user_id: int | None = None,
        family_id: int | None = None,
        # TODO: убрать если нет взаимосвязи между user_id и family_id в одной сущности
        namespace_type: NamespaceType = NamespaceType.GLOBAL,
    ) -> str:
        """
        Формирует пространство имен.

        Args:
            user_id: ID пользователя
            family_id: ID семьи
            namespace_type: Тип пространства имен

        Returns:
            str: Имя пространства имен

        Приоритет:
            1. Если указан user_id -> user:{user_id}
            2. Если указан family_id -> family:{family_id}
            3. Иначе -> global
        """
        if user_id is not None:
            return f"user:{user_id}"
        elif family_id is not None:
            return f"family:{family_id}"
        else:
            return "global"

    def _get_namespace_data(self, namespace: str) -> dict[str, CacheEntry]:
        """Получает или создает пространство имен."""
        if namespace not in self._data:
            self._data[namespace] = {}
        return self._data[namespace]

    def _extract_id_from_namespace(
        self, namespace: str
    ) -> tuple[NamespaceType, int | None]:
        """
        Извлекает тип и ID из пространства имен.

        Args:
            namespace: Имя пространства имен

        Returns:
            tuple[NamespaceType, Optional[int]]: Тип и ID
        """
        if namespace == "global":
            return NamespaceType.GLOBAL, None

        parts = namespace.split(":")
        if len(parts) == 2:
            namespace_type = parts[0]
            try:
                entity_id = int(parts[1])
                if namespace_type == "user":
                    return NamespaceType.USER, entity_id
                elif namespace_type == "family":
                    return NamespaceType.FAMILY, entity_id
            except ValueError:
                pass

        return NamespaceType.GLOBAL, None

    # ========== Основные методы ==========

    async def get(
        self, key: str, user_id: int | None = None, family_id: int | None = None
    ) -> str | None:
        """
        Получает значение по ключу.

        Args:
            key: Ключ для поиска
            user_id: ID пользователя (опционально)
            family_id: ID семьи (опционально)

        Returns:
            Optional[str]: Значение или None, если не найдено или просрочено
        """
        namespace = self._get_namespace(user_id=user_id, family_id=family_id)
        namespace_data = self._data.get(namespace, {})

        entry = namespace_data.get(key)
        if entry is None:
            return None

        if entry.is_expired:
            # Удаляем просроченную запись
            del namespace_data[key]
            if not namespace_data:
                del self._data[namespace]
            return None

        return entry.value

    async def set(
        self,
        key: str,
        value: str,
        ttl: int | None = None,
        user_id: int | None = None,
        family_id: int | None = None,
    ) -> None:
        """
        Устанавливает значение по ключу.

        Args:
            key: Ключ
            value: Значение
            ttl: Время жизни в секундах (None = бесконечно)
            user_id: ID пользователя (опционально)
            family_id: ID семьи (опционально)
        """
        namespace = self._get_namespace(user_id=user_id, family_id=family_id)
        namespace_data = self._get_namespace_data(namespace)

        expires_at = None
        if ttl is not None:
            expires_at = time.time() + ttl

        namespace_data[key] = CacheEntry(value=value, expires_at=expires_at)

    async def delete(
        self, key: str, user_id: int | None = None, family_id: int | None = None
    ) -> bool:
        """
        Удаляет запись по ключу.

        Args:
            key: Ключ для удаления
            user_id: ID пользователя (опционально)
            family_id: ID семьи (опционально)

        Returns:
            bool: True если запись была удалена
        """
        namespace = self._get_namespace(user_id=user_id, family_id=family_id)
        namespace_data = self._data.get(namespace, {})

        if key in namespace_data:
            del namespace_data[key]
            if not namespace_data:
                del self._data[namespace]
            return True

        return False

    async def get_all(
        self, user_id: int | None = None, family_id: int | None = None
    ) -> dict[str, str]:
        """
        Возвращает все записи в пространстве имен.

        Args:
            user_id: ID пользователя (опционально)
            family_id: ID семьи (опционально)

        Returns:
            Dict[str, str]: Словарь всех не просроченных записей
        """
        namespace = self._get_namespace(user_id=user_id, family_id=family_id)
        namespace_data = self._data.get(namespace, {})

        result = {}
        expired_keys = []

        for k, entry in namespace_data.items():
            if entry.is_expired:
                expired_keys.append(k)
                continue
            result[k] = entry.value

        # Удаляем просроченные записи
        for k in expired_keys:
            del namespace_data[k]

        if not namespace_data:
            self._data.pop(namespace, None)

        return result

    # ========== Методы для работы с пользователями ==========

    async def get_user_session(self, user_id: int) -> dict[str, str]:
        """
        Получает все данные сессии пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            Dict[str, str]: Данные сессии
        """
        return await self.get_all(user_id=user_id)

    async def clear_user_session(self, user_id: int) -> bool:
        """
        Очищает все данные пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            bool: True если данные были удалены
        """
        namespace = self._get_namespace(user_id=user_id)
        if namespace in self._data:
            del self._data[namespace]
            return True
        return False

    async def get_user_state(self, user_id: int) -> str | None:
        """
        Получает состояние FSM пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            Optional[str]: Состояние или None
        """
        return await self.get("state", user_id=user_id)

    async def set_user_state(
        self, user_id: int, state: str, ttl: int | None = 3600
    ) -> None:
        """
        Устанавливает состояние FSM пользователя.

        Args:
            user_id: ID пользователя
            state: Состояние
            ttl: Время жизни в секундах (по умолчанию 1 час)
        """
        await self.set("state", state, ttl=ttl, user_id=user_id)

    # ========== Методы для работы с семьями ==========

    async def get_family_data(self, family_id: int) -> dict[str, str]:
        """
        Получает все данные семьи.

        Args:
            family_id: ID семьи

        Returns:
            Dict[str, str]: Данные семьи
        """
        return await self.get_all(family_id=family_id)

    async def clear_family_data(self, family_id: int) -> bool:
        """
        Очищает все данные семьи.

        Args:
            family_id: ID семьи

        Returns:
            bool: True если данные были удалены
        """
        namespace = self._get_namespace(family_id=family_id)
        if namespace in self._data:
            del self._data[namespace]
            return True
        return False

    async def get_family_members(self, family_id: int) -> str | None:
        """
        Получает список участников семьи.

        Args:
            family_id: ID семьи

        Returns:
            Optional[str]: JSON строка с участниками или None
        """
        return await self.get("members", family_id=family_id)

    async def set_family_members(
        self, family_id: int, members_json: str, ttl: int | None = None
    ) -> None:
        """
        Устанавливает список участников семьи.

        Args:
            family_id: ID семьи
            members_json: JSON строка с участниками
            ttl: Время жизни в секундах
        """
        await self.set("members", members_json, ttl=ttl, family_id=family_id)

    async def get_family_settings(self, family_id: int) -> str | None:
        """
        Получает настройки семьи.

        Args:
            family_id: ID семьи

        Returns:
            Optional[str]: JSON строка с настройками или None
        """
        return await self.get("settings", family_id=family_id)

    async def set_family_settings(
        self, family_id: int, settings_json: str, ttl: int | None = None
    ) -> None:
        """
        Устанавливает настройки семьи.

        Args:
            family_id: ID семьи
            settings_json: JSON строка с настройками
            ttl: Время жизни в секундах
        """
        await self.set("settings", settings_json, ttl=ttl, family_id=family_id)

    # ========== Методы для работы с глобальными данными ==========

    async def get_global(self, key: str) -> str | None:
        """Получает глобальное значение."""
        return await self.get(key)

    async def set_global(self, key: str, value: str, ttl: int | None = None) -> None:
        """Устанавливает глобальное значение."""
        await self.set(key, value, ttl=ttl)

    async def clear_global(self) -> bool:
        """Очищает глобальные данные."""
        namespace = self._get_namespace()
        if namespace in self._data:
            del self._data[namespace]
            return True
        return False

    # ========== Методы для статистики ==========

    async def clear_expired(self) -> int:
        """
        Принудительная очистка всех просроченных записей.

        Returns:
            int: Количество удаленных записей
        """
        count = 0
        for namespace in list(self._data.keys()):
            namespace_data = self._data[namespace]
            expired_keys = [
                key for key, entry in namespace_data.items() if entry.is_expired
            ]

            for key in expired_keys:
                del namespace_data[key]
                count += 1

            if not namespace_data:
                del self._data[namespace]

        return count

    async def get_stats(self) -> dict[str, Any]:
        """
        Возвращает статистику кэша.

        Returns:
            Dict[str, Any]: Статистика
        """
        total_entries = 0
        total_expired = 0
        user_namespaces = 0
        family_namespaces = 0
        global_entries = 0

        for namespace, data in self._data.items():
            total_entries += len(data)

            if namespace.startswith("user:"):
                user_namespaces += 1
            elif namespace.startswith("family:"):
                family_namespaces += 1
            elif namespace == "global":
                global_entries = len(data)

            total_expired += sum(1 for entry in data.values() if entry.is_expired)

        return {
            "total_namespaces": len(self._data),
            "user_namespaces": user_namespaces,
            "family_namespaces": family_namespaces,
            "global_entries": global_entries,
            "total_entries": total_entries,
            "expired_entries": total_expired,
            "memory_usage_bytes": self._estimate_memory_usage(),
        }

    def _estimate_memory_usage(self) -> int:
        """Оценивает использование памяти в байтах."""
        import sys

        total = 0
        for namespace, data in self._data.items():
            total += sys.getsizeof(namespace)
            for key, entry in data.items():
                total += sys.getsizeof(key)
                total += sys.getsizeof(entry.value)
                total += sys.getsizeof(entry)
        return total

    # ========== Вспомогательные методы ==========

    async def delete_by_pattern(self, pattern: str) -> int:
        """
        Удаляет все записи, ключи которых соответствуют паттерну.

        Args:
            pattern: Паттерн для поиска (например, "user:*" или "family:123:*")

        Returns:
            int: Количество удаленных записей
        """
        import fnmatch

        count = 0
        namespaces_to_delete = []

        for namespace in self._data:
            if fnmatch.fnmatch(namespace, pattern):
                namespaces_to_delete.append(namespace)

        for namespace in namespaces_to_delete:
            count += len(self._data[namespace])
            del self._data[namespace]

        return count

    async def get_namespaces(self) -> list[str]:
        """Возвращает список всех пространств имен."""
        return list(self._data.keys())

    async def get_namespace_info(self, namespace: str) -> dict[str, Any]:
        """
        Возвращает информацию о пространстве имен.

        Args:
            namespace: Имя пространства имен

        Returns:
            Dict[str, Any]: Информация о пространстве
        """
        if namespace not in self._data:
            return {"exists": False}

        namespace_type, entity_id = self._extract_id_from_namespace(namespace)
        data = self._data[namespace]

        return {
            "exists": True,
            "type": namespace_type.value,
            "entity_id": entity_id,
            "entries_count": len(data),
            "entries": list(data.keys()),
            "expired_count": sum(1 for entry in data.values() if entry.is_expired),
        }
