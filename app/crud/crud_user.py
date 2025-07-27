from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel # Используем для заглушек в Generic
# Импортируем нашу функцию для проверки пароля и базовый класс CRUD
from app.core.security import verify_password
from app.crud.base import CRUDBase
from app.models.user import User

class CRUDUser(CRUDBase[User, BaseModel, BaseModel]):
    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        result = await db.execute(select(self.model).filter(self.model.username == username))
        return result.scalars().first()

    async def authenticate(self, db: AsyncSession, *, username: str, password: str) -> Optional[User]:
        user = await self.get_by_username(db, username=username)

        # Если пользователь не найден, выходим
        if not user:
            return None

        # Шаг 2: проверяем пароль.
        # Хеширование - это CPU-bound операция, ей await не нужен.
        if not verify_password(password, user.hashed_password):
            return None

        # Если все проверки пройдены, возвращаем пользователя
        return user

user = CRUDUser(User)