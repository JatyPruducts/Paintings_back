from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# импортируем метадату моделей
from app.db.base import Base
from app.models.painting import Painting
from app.models.user_session import UserSession
from app.models.feedback import Feedback
from app.models.user import User

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata
database_url = os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url")

if not database_url:
    try:
        # Попытаться получить из app.core.config (если доступно)
        from app.core.config import settings
        database_url = str(settings.DATABASE_URL)
    except Exception:
        # если даже это не удалось — оставим database_url пустым и Alembic
        # будет использовать то, что в alembic.ini (если там указан)
        database_url = None

if database_url:
    # Если в проекте используется asyncpg в DATABASE_URL, преобразуем в sync драйвер для alembic
    if database_url.startswith("postgresql+asyncpg"):
        sync_db_url = database_url.replace("postgresql+asyncpg", "postgresql+psycopg2")
    else:
        sync_db_url = database_url

    # Подставим полученный URL в конфиг alembic
    config.set_main_option("sqlalchemy.url", sync_db_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()