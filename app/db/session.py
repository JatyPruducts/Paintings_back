# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

# Создаем асинхронный "движок" для взаимодействия с базой данных.
# 'pool_pre_ping=True' проверяет соединение перед каждым запросом.
engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Создаем "фабрику" для асинхронных сессий.
# autocommit=False и autoflush=False — стандартные и безопасные настройки.
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)