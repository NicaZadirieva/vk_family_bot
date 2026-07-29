import logging
import logging.config
from pathlib import Path

import yaml

from app.settings import settings


class LoggerUtils:
    @staticmethod
    def setup_logger():
        """
        Настройка логирования на основе log_conf.yaml и параметров из .env.
        """
        # Получаем параметры из настроек
        environment = settings.common_app.ENVIRONMENT
        # Создаём директорию для логов, если её нет
        if environment == "development":
            Path("logs/dev/").mkdir(parents=True, exist_ok=True)
        if environment == "production":
            Path("logs/prod/").mkdir(parents=True, exist_ok=True)

        # Загружаем конфигурацию из YAML
        config_path = Path(
            f"log_conf.{environment.lower()}.yaml"
        )  # или укажите полный путь
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

            # Применяем конфигурацию
            logging.config.dictConfig(config)

            # 4. Отдельная настройка уровней для сторонних библиотек
            logging.getLogger("apscheduler").setLevel(logging.WARNING)
            logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
            logging.getLogger("aiohttp").setLevel(logging.WARNING)
            logging.getLogger("chardet").setLevel(logging.WARNING)
            logging.getLogger("app.controllers.vk_client").setLevel(logging.WARNING)
