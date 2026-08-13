from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import settings
from app.settings import settings  # noqa: F811

engine = create_async_engine(
    settings.db.DATABASE_URL,
    echo=False,  # вывод sql-команд отключена
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,  # создание новой сессии после каждого коммита в БД отключена
)
