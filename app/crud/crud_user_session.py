from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession # <-- 1. Используем асинхронную сессию
from pydantic import BaseModel
from app.crud.base import CRUDBase
from app.models.user_session import UserSession
from app.schemas.user_session import UserSessionCreate


class CRUDUserSession(CRUDBase[UserSession, UserSessionCreate, BaseModel]):

    async def count(self, db: AsyncSession) -> int: # <-- 2. Объявляем как async def
        """
        Специфичный асинхронный метод для подсчета общего числа сессий.
        """
        # 3. Используем асинхронный синтаксис с db.execute и select()
        result = await db.execute(select(func.count(self.model.id)))
        # .scalar() извлекает единственный результат из ответа
        return result.scalar()


user_session = CRUDUserSession(UserSession)