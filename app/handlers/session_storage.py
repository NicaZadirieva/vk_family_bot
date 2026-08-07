import json
from typing import Any

import redis


class SessionStorage:
    """Универсальное хранилище сессий с поддержкой dict и Redis"""

    def __init__(self, vk_id: int, use_redis: bool = True, ttl: int = 3600):
        """
        Args:
            vk_id: ID пользователя ВКонтакте
            use_redis: Если False - использует dict (для тестов), True - Redis
            ttl: Время жизни сессии в секундах (по умолчанию 1 час)
        """
        self.vk_id = vk_id
        self._use_redis = use_redis
        self._ttl = ttl
        self._key = f"session:{vk_id}"

        # Для обратной совместимости с вашим текущим кодом
        self._dict_cache: dict[str, Any] = {}

        if use_redis:
            self._redis = redis.Redis(
                host="localhost",
                port=6379,
                db=0,
                decode_responses=True,  # Автоматически декодировать байты в строки
            )
        else:
            self._redis = None

    # ==================== Базовые операции ====================

    def get(self, field: str, default: Any = None) -> Any:
        """Получить значение поля"""
        if self._use_redis and self._redis:
            value = self._redis.hget(self._key, field)
            if value is None:
                return default
            # Попытка распарсить JSON, если это не строка
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        else:
            return self._dict_cache.get(field, default)

    def set(self, field: str, value: Any) -> int:
        """Установить значение поля"""
        # Подготовка значения для хранения
        if isinstance(value, (dict, list, tuple, set)):
            stored_value = json.dumps(value, ensure_ascii=False)
        else:
            stored_value = (
                str(value) if not isinstance(value, (int, float, bool)) else value
            )

        if self._use_redis and self._redis:
            result = self._redis.hset(self._key, field, stored_value)
            # Обновляем TTL при каждом изменении
            self._redis.expire(self._key, self._ttl)
            return result
        else:
            self._dict_cache[field] = value
            return True

    def delete(self, field: str) -> bool:
        """Удалить поле"""
        if self._use_redis and self._redis:
            return bool(self._redis.hdel(self._key, field))
        else:
            if field in self._dict_cache:
                del self._dict_cache[field]
                return True
            return False

    def exists(self, field: str) -> bool:
        """Проверить существование поля"""
        if self._use_redis and self._redis:
            return self._redis.hexists(self._key, field)
        else:
            return field in self._dict_cache

    # ==================== Массовые операции ====================

    def get_all(self) -> dict[str, Any]:
        """Получить все поля сессии"""
        if self._use_redis and self._redis:
            data = self._redis.hgetall(self._key)
            # Парсим JSON-значения
            result = {}
            for key, value in data.items():
                try:
                    result[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    result[key] = value
            return result
        else:
            return self._dict_cache.copy()

    def set_multiple(self, mapping: dict[str, Any]) -> bool:
        """Установить несколько полей одновременно"""
        # Подготовка данных
        prepared = {}
        for key, value in mapping.items():
            if isinstance(value, (dict, list, tuple, set)):
                prepared[key] = json.dumps(value, ensure_ascii=False)
            else:
                prepared[key] = (
                    str(value) if not isinstance(value, (int, float, bool)) else value
                )

        if self._use_redis and self._redis:
            result = self._redis.hset(self._key, mapping=prepared)
            self._redis.expire(self._key, self._ttl)
            return bool(result)
        else:
            self._dict_cache.update(mapping)
            return True

    def delete_multiple(self, *fields: str) -> int:
        """Удалить несколько полей"""
        if self._use_redis and self._redis:
            if fields:
                return self._redis.hdel(self._key, *fields)
            return 0
        else:
            count = 0
            for field in fields:
                if field in self._dict_cache:
                    del self._dict_cache[field]
                    count += 1
            return count

    # ==================== Работа со временем ====================

    def get_ttl(self) -> int:
        """Получить оставшееся время жизни сессии в секундах"""
        if self._use_redis and self._redis:
            ttl = self._redis.ttl(self._key)
            return max(0, ttl)
        return self._ttl  # Для dict возвращаем установленный TTL

    def update_ttl(self, ttl: int | None = None) -> bool:
        """Обновить время жизни сессии"""
        ttl = ttl or self._ttl
        if self._use_redis and self._redis:
            return bool(self._redis.expire(self._key, ttl))
        else:
            self._ttl = ttl
            return True

    def touch(self) -> bool:
        """Продлить жизнь сессии (обновить TTL)"""
        return self.update_ttl()

    # ==================== Инкремент/декремент ====================

    def increment(self, field: str, amount: int = 1) -> int | float:
        """Увеличить числовое поле"""
        if self._use_redis and self._redis:
            # Redis HINCRBY работает только с целыми числами
            current = self.get(field, 0)
            if not isinstance(current, (int, float)):
                current = 0
            new_value = current + amount
            self.set(field, new_value)
            return new_value
        else:
            current = self._dict_cache.get(field, 0)
            if not isinstance(current, (int, float)):
                current = 0
            new_value = current + amount
            self._dict_cache[field] = new_value
            return new_value

    # ==================== Утилиты для ботов ====================

    def clear(self) -> bool:
        """Полностью очистить сессию"""
        if self._use_redis and self._redis:
            return bool(self._redis.delete(self._key))
        else:
            self._dict_cache.clear()
            return True

    def get_state(self) -> str | None:
        """Получить текущее состояние диалога (FSM)"""
        return self.get("state")

    def set_state(self, state: str) -> int:
        """Установить состояние диалога"""
        return self.set("state", state)

    def get_context(self) -> dict[str, Any]:
        """
        Получить полный контекст (для вашей функции __get_data_from_context__)
        """
        return self.get_all()

    def update_context(self, **kwargs) -> bool:
        """Обновить контекст несколькими полями"""
        return self.set_multiple(kwargs)

    # ==================== Магические методы ====================

    def __getitem__(self, field: str) -> Any:
        """Поддержка session['field']"""
        value = self.get(field)
        if value is None:
            raise KeyError(f"Field '{field}' not found")
        return value

    def __setitem__(self, field: str, value: Any):
        """Поддержка session['field'] = value"""
        self.set(field, value)

    def __delitem__(self, field: str):
        """Поддержка del session['field']"""
        self.delete(field)

    def __contains__(self, field: str) -> bool:
        """Поддержка 'field' in session"""
        return self.exists(field)

    def __repr__(self) -> str:
        return f"<SessionStorage(vk_id={self.vk_id}, key='{self._key}', use_redis={self._use_redis})>"


# ==================== Фабрика для удобного создания ====================


class SessionFactory:
    """Фабрика для создания хранилищ сессий"""

    def __init__(self, use_redis: bool = True, default_ttl: int = 3600):
        self.use_redis = use_redis
        self.default_ttl = default_ttl

    def get_session(self, vk_id: int, ttl: int | None = None) -> SessionStorage:
        """Получить сессию пользователя"""
        return SessionStorage(
            vk_id=vk_id, use_redis=self.use_redis, ttl=ttl or self.default_ttl
        )
