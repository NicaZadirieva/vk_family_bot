import re


class VkUtils:
    @staticmethod
    def is_valid_vk_id(vk_id: str) -> bool:
        """
        Проверяет, является ли строка корректным VK ID.

        Правила для VK ID:
        - Может быть числовым (например: 123456789)
        - Может быть строковым (например: id123456789 или durov)
        - Не может быть пустым
        - Не может содержать пробелы
        - Минимальная длина: 1 символ (для строковых ID)
        """
        if not vk_id:
            return False

        # Проверка на наличие пробелов
        if " " in vk_id:
            return False

        # Проверка на допустимые символы
        # Разрешены: латиница, цифры, нижнее подчеркивание, точка, дефис
        # Также допустим префикс 'id' перед цифрами
        pattern = r"^(?:id)?[a-zA-Z0-9._-]+$"

        if not re.match(pattern, vk_id):
            return False

        # Дополнительные проверки
        # Если ID начинается с 'id', то после должны идти только цифры
        if vk_id.startswith("id"):
            rest = vk_id[2:]
            if rest and not rest.isdigit():
                return False

        # Проверка максимальной длины (обычно VK ID не длиннее 50 символов)
        return not len(vk_id) > 50
