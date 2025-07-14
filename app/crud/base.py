from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy import select
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import Base

# Определяем кастомные типы для моделей и схем
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Базовый CRUD-класс с методами по умолчанию для Create, Read, Update, Delete.
    """

    def __init__(self, model: Type[ModelType]):
        """
        CRUD-объект с базовыми методами для работы с моделью SQLAlchemy.

        **Параметры**
        * `model`: SQLAlchemy модель
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Асинхронное получение одной записи по ID."""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получить несколько записей с пагинацией."""
        result = await db.execute(
            select(self.model).order_by(self.model.id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Создать новую запись."""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        await db.commit()  # Коммит сессии
        await db.refresh(db_obj)  # Обновление объекта
        return db_obj

    async def update(
            self,
            db: Session,
            *,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Обновить существующую запись."""
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        await db.commit()  # Коммит сессии
        await db.refresh(db_obj)  # Обновление объекта
        return db_obj

    async def remove(self, db: Session, *, id: int) -> ModelType:
        """Удалить запись."""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        obj = result.scalars().first()
        if obj:
            await db.delete(obj)
            await db.commit()  # Коммит сессии
        return obj