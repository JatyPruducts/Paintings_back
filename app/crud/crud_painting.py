from typing import List, Optional
from app.crud.base import CRUDBase
from app.models.painting import Painting
from app.schemas.painting import PaintingCreate, PaintingUpdate
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDPainting(CRUDBase[Painting, PaintingCreate, PaintingUpdate]):

    def _apply_filters(
            self,
            query,  # Объект запроса SQLAlchemy
            title: Optional[str] = None,
            tags: Optional[List[str]] = None,
            width_min: Optional[float] = None,
            width_max: Optional[float] = None,
            height_min: Optional[float] = None,
            height_max: Optional[float] = None,
    ):
        """Вспомогательный метод для применения фильтров к запросу."""
        if title:
            # ilike для регистронезависимого поиска
            query = query.filter(self.model.title.ilike(f"%{title}%"))

        if tags:
            # .contains для поиска в массивах PostgreSQL.
            # Он проверяет, содержит ли массив `tags` в БД ВСЕ теги из списка.
            query = query.filter(self.model.tags.overlap(tags))

        if width_min is not None:
            query = query.filter(self.model.width >= width_min)

        if width_max is not None:
            query = query.filter(self.model.width <= width_max)

        if height_min is not None:
            query = query.filter(self.model.height >= height_min)

        if height_max is not None:
            query = query.filter(self.model.height <= height_max)

        return query

    async def get_multi_filtered(
            self,
            db: AsyncSession,
            *,
            skip: int = 0,
            limit: int = 12,
            title: Optional[str] = None,
            tags: Optional[List[str]] = None,
            width_min: Optional[float] = None,
            width_max: Optional[float] = None,
            height_min: Optional[float] = None,
            height_max: Optional[float] = None,
    ) -> List[Painting]:
        """Получить список картин с фильтрацией и пагинацией."""
        query = select(self.model)
        query = self._apply_filters(
            query, title=title, tags=tags,
            width_min=width_min, width_max=width_max,
            height_min=height_min, height_max=height_max
        )

        query = query.order_by(self.model.id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def count_filtered(
            self,
            db: AsyncSession,
            *,
            title: Optional[str] = None,
            tags: Optional[List[str]] = None,
            width_min: Optional[float] = None,
            width_max: Optional[float] = None,
            height_min: Optional[float] = None,
            height_max: Optional[float] = None,
    ) -> int:
        """Подсчитать количество картин с учетом фильтров."""
        # Начинаем с запроса на подсчет
        query = select(func.count(self.model.id))
        query = self._apply_filters(
            query, title=title, tags=tags,
            width_min=width_min, width_max=width_max,
            height_min=height_min, height_max=height_max
        )

        result = await db.execute(query)
        return result.scalar_one()

    async def get_all_tags(self, db: AsyncSession) -> List[str]:
        """Получает отсортированный список всех уникальных тегов."""
        query = select(func.distinct(func.unnest(self.model.tags))).order_by(
            func.unnest(self.model.tags)
        )
        result = await db.execute(query)
        tags = result.scalars().all()
        return tags


# Создаем единый экземпляр класса
painting = CRUDPainting(Painting)