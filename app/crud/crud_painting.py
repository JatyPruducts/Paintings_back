from app.crud.base import CRUDBase
from app.models.painting import Painting
from app.schemas.painting import PaintingCreate, PaintingUpdate
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

# Создаем класс для картин, наследуясь от базового
class CRUDPainting(CRUDBase[Painting, PaintingCreate, PaintingUpdate]):

    async def count(self, db: AsyncSession) -> int:
        """
        Асинхронно подсчитывает общее количество картин в базе данных.
        """
        result = await db.execute(select(func.count(self.model.id)))
        # .scalar_one() извлекает единственный результат (число)
        return result.scalar_one()

# Создаем единый экземпляр класса для использования во всем приложении
painting = CRUDPainting(Painting)