import asyncio
import argparse
import sys
from pathlib import Path

# --- Настройка пути для импорта из папки 'app' ---
# Этот скрипт находится вне папки 'app', поэтому Python по умолчанию не сможет
# найти модули вроде 'app.db'. Этот код добавляет корневую папку проекта
# в список путей, которые Python просматривает при импорте.
current_path = Path(__file__).parent.parent
sys.path.append(str(current_path))

# --- Основные импорты из нашего приложения ---
from app.db.session import SessionLocal  # Наша фабрика асинхронных сессий
from app.models.user import User         # Модель пользователя
from app.core.security import get_password_hash # Функция для хеширования пароля
from sqlalchemy import select

async def main():
    """
    Основная асинхронная функция для создания суперпользователя.
    """
    # 1. Настраиваем парсер для аргументов командной строки (чтобы можно было
    # передать --username и --password при запуске скрипта)
    parser = argparse.ArgumentParser(description="Create a new superuser.")
    parser.add_argument(
        "--username",
        type=str,
        required=True,
        help="The username for the new superuser."
    )
    parser.add_argument(
        "--password",
        type=str,
        required=True,
        help="The password for the new superuser."
    )
    args = parser.parse_args()

    print(f"Attempting to create superuser '{args.username}'...")

    # 2. Создаем асинхронную сессию для работы с базой данных
    async with SessionLocal() as db:
        # Проверяем, не существует ли уже пользователь с таким именем
        result = await db.execute(select(User).filter(User.username == args.username))
        existing_user = result.scalars().first()

        if existing_user:
            print(f"Error: User with username '{args.username}' already exists.")
            return # Выходим, если пользователь найден

        # 3. Хешируем пароль
        hashed_password = get_password_hash(args.password)

        # 4. Создаем новый объект пользователя на основе модели User
        # Обязательно устанавливаем is_superuser=True
        db_user = User(
            username=args.username,
            hashed_password=hashed_password,
            is_superuser=True,
        )

        # 5. Добавляем пользователя в сессию и сохраняем изменения в БД
        db.add(db_user)
        await db.commit()

        print(f"Superuser '{args.username}' created successfully!")


# Стандартная точка входа для запуска асинхронной функции 'main'
if __name__ == "__main__":
    asyncio.run(main())