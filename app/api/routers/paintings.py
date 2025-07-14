from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import math

# Разделяем импорты для ясности
from app import crud
from app.models.user import User
from app.schemas.painting import PaintingInDB, PaintingCreate, PaintingUpdate, TotalPagesResponse
from app.api import deps

router = APIRouter()


# --- Публичные эндпоинты (доступны всем) ---

@router.get("/", response_model=List[PaintingInDB])
async def read_paintings(
        db: AsyncSession = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 12  # По умолчанию 12 картин, как в вашем прототипе
):
    """
    Получить список всех картин с пагинацией.
    """
    paintings = await crud.painting.get_multi(db, skip=skip, limit=limit)
    return paintings


@router.get("/pages/total", response_model=TotalPagesResponse)
async def get_total_pages(db: AsyncSession = Depends(deps.get_db)):
    """
    Получить общее количество страниц с картинами (по 12 на страницу).
    """
    page_size = 12
    total_paintings = await crud.painting.count(db=db)

    # С помощью math.ceil() округляем результат деления вверх
    # Например, 25 картин / 12 = 2.08 -> 3 страницы
    # 24 картины / 12 = 2.0 -> 2 страницы
    total_pages = math.ceil(total_paintings / page_size)

    return {"total_pages": total_pages}


@router.get("/{painting_id}", response_model= PaintingInDB)
async def read_painting_by_id(
        painting_id: int,
        db: AsyncSession = Depends(deps.get_db)
):
    """
    Получить одну картину по ее ID.
    """
    db_painting = await crud.painting.get(db, id=painting_id)
    if db_painting is None:
        raise HTTPException(status_code=404, detail="Painting not found")
    return db_painting



# --- Защищенные эндпоинты (только для администратора) ---

@router.post("/", response_model= PaintingInDB, status_code=status.HTTP_201_CREATED)
async def create_painting(
        *,
        db: AsyncSession = Depends(deps.get_db),
        painting_in: PaintingCreate,
        current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Создать новую картину. Требуются права суперпользователя.
    """
    new_painting = await crud.painting.create(db=db, obj_in=painting_in)
    return new_painting


@router.put("/{painting_id}", response_model= PaintingInDB)
async def update_painting(
        *,
        db: AsyncSession = Depends(deps.get_db),
        painting_id: int,
        painting_in: PaintingUpdate,
        current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Обновить существующую картину. Требуются права суперпользователя.
    """
    db_painting = await crud.painting.get(db, id=painting_id)
    if not db_painting:
        raise HTTPException(status_code=404, detail="Painting not found")

    updated_painting = await crud.painting.update(db=db, db_obj=db_painting, obj_in=painting_in)
    return updated_painting


@router.delete("/{painting_id}", response_model= PaintingInDB)
async def delete_painting(
        *,
        db: AsyncSession = Depends(deps.get_db),
        painting_id: int,
        current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Удалить картину. Требуются права суперпользователя.
    """
    db_painting = await crud.painting.get(db, id=painting_id)
    if not db_painting:
        raise HTTPException(status_code=404, detail="Painting not found")

    deleted_painting = await crud.painting.remove(db=db, id=painting_id)
    return deleted_painting