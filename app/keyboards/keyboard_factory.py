import json
from typing import Dict, Any, Optional


class KeyboardFactory:
    """
    Простая фабрика для создания клавиатур VK.
    Только создание структур, без бизнес-логики.
    """

    @staticmethod
    def create(screen_type: str) -> Optional[Dict[str, Any]]:
        """
        Создание клавиатуры по типу экрана.

        Returns:
            Dict с клавиатурой или None
        """
        # Карта соответствия screen_type -> функция создания
        keyboards = {}

        # Возвращаем клавиатуру или None (без клавиатуры)
        if screen_type in keyboards:
            return keyboards[screen_type]()

        # По умолчанию - только "Назад"
        return KeyboardFactory._back_only()

    @staticmethod
    def _btn(label: str, action: str, color: str = "secondary") -> Dict[str, Any]:
        """
        Создание кнопки.

        Args:
            label: Текст на кнопке
            action: Действие (будет в payload)
            color: Цвет кнопки (primary, secondary, positive, negative)
        """
        return {
            "action": {
                "type": "text",
                "label": label,
                "payload": json.dumps({"action": action}),
            },
            "color": color,
        }

    @staticmethod
    def _back_only() -> Dict[str, Any]:
        """Только кнопка 'Назад'."""
        return {
            "one_time": False,
            "buttons": [[KeyboardFactory._btn("🔙 Назад", "back", "secondary")]],
        }

    @staticmethod
    def _cancel_only() -> Dict[str, Any]:
        """Только кнопка 'Отмена'."""
        return {
            "one_time": False,
            "buttons": [[KeyboardFactory._btn("❌ Отмена", "cancel", "negative")]],
        }
