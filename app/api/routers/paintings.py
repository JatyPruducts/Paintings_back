import os
import shutil
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import math

from app import crud
from app.models.user import User
from app.schemas.painting import PaintingInDB, PaintingCreate, PaintingUpdate, TotalPagesResponse
from app.api import deps

router = APIRouter()

# Определяем путь к папке для загрузок
UPLOADS_DIR = "static/uploads"
# Создаем папку, если ее нет
os.makedirs(UPLOADS_DIR, exist_ok=True)


# --- Публичные эндпоинты---
@router.get("/", response_model=List[PaintingInDB])
async def read_paintings(
        db: AsyncSession = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 12
):
    paintings = await crud.painting.get_multi(db, skip=skip, limit=limit)
    return paintings

@router.get("/pages/total", response_model=TotalPagesResponse)
async def get_total_pages(db: AsyncSession = Depends(deps.get_db)):
    page_size = 12
    total_paintings = await crud.painting.count(db=db)
    total_pages = math.ceil(total_paintings / page_size)
    return {"total_pages": total_pages}

@router.get("/{painting_id}", response_model=PaintingInDB)
async def read_painting_by_id(
        painting_id: int,
        db: AsyncSession = Depends(deps.get_db)
):
    db_painting = await crud.painting.get(db, id=painting_id)
    if db_painting is None:
        raise HTTPException(status_code=404, detail="Painting not found")
    return db_painting


# --- Защищенные эндпоинты (модифицированы) ---

@router.post("/", response_model=PaintingInDB, status_code=status.HTTP_201_CREATED)
async def create_painting(
        *,
        db: AsyncSession = Depends(deps.get_db),
        title: str = Form(...),
        width: float = Form(...),
        height: float = Form(...),
        tags: str = Form(...),  # Тэги придут как строка "море,закат"
        description: str = Form(""),
        images: List[UploadFile] = File(...),
        current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Создать новую картину. Требуются права суперпользователя.
    Принимает данные в формате multipart/form-data.
    """
    if not images:
        raise HTTPException(status_code=400, detail="No images uploaded.")

    saved_filenames = []
    for image in images:
        # Генерируем уникальное имя файла, чтобы избежать конфликтов
        extension = image.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{extension}"
        file_path = os.path.join(UPLOADS_DIR, unique_filename)

        # Сохраняем файл на диск
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            saved_filenames.append(f"/static/uploads/{unique_filename}") # <-- Сохраняем полный путь
        finally:
            image.file.close()

    # Преобразуем строку тегов в список
    tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]

    # Создаем Pydantic схему для передачи в CRUD-операцию
    painting_in = PaintingCreate(
        title=title,
        width=width,
        height=height,
        tags=tags_list,
        description=description,
        photo_filenames=saved_filenames # Используем список сохраненных имен файлов
    )

    new_painting = await crud.painting.create(db=db, obj_in=painting_in)
    return new_painting


@router.put("/{painting_id}", response_model=PaintingInDB)
async def update_painting(
        *,
        db: AsyncSession = Depends(deps.get_db),
        painting_id: int,
        title: str = Form(...),
        width: float = Form(...),
        height: float = Form(...),
        tags: str = Form(...),
        description: str = Form(""),
        # Файлы опциональны: если не прислали, значит не меняем
        images: Optional[List[UploadFile]] = File(None),
        current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Обновить существующую картину.
    Если переданы новые файлы, они полностью заменяют старые.
    """
    db_painting = await crud.painting.get(db, id=painting_id)
    if not db_painting:
        raise HTTPException(status_code=404, detail="Painting not found")

    # Преобразуем строку тегов в список
    tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]

    # Собираем данные для обновления
    update_data = {
        "title": title,
        "width": width,
        "height": height,
        "tags": tags_list,
        "description": description,
    }

    # Если были загружены новые файлы
    if images:
        # 1. Удаляем старые файлы с диска
        for old_filename in db_painting.photo_filenames:
            # Убираем /static/uploads/ из пути, чтобы получить имя файла
            file_to_delete = old_filename.replace('/static/uploads/', '')
            old_file_path = os.path.join(UPLOADS_DIR, file_to_delete)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

        # 2. Сохраняем новые файлы
        saved_filenames = []
        for image in images:
            extension = image.filename.split(".")[-1]
            unique_filename = f"{uuid.uuid4()}.{extension}"
            file_path = os.path.join(UPLOADS_DIR, unique_filename)
            try:
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                saved_filenames.append(f"/static/uploads/{unique_filename}")
            finally:
                image.file.close()

        # 3. Добавляем список новых файлов в данные для обновления
        update_data["photo_filenames"] = saved_filenames

    # Создаем схему и обновляем запись в БД
    painting_in = PaintingUpdate(**update_data)
    updated_painting = await crud.painting.update(db=db, db_obj=db_painting, obj_in=painting_in)
    return updated_painting

@router.delete("/{painting_id}", response_model=PaintingInDB)
async def delete_painting(
        *,
        db: AsyncSession = Depends(deps.get_db),
        painting_id: int,
        current_user: User = Depends(deps.get_current_active_superuser)
):
    db_painting = await crud.painting.get(db, id=painting_id)
    if not db_painting:
        raise HTTPException(status_code=404, detail="Painting not found")

    # Удаляем файлы с диска перед удалением записи из БД
    for filename in db_painting.photo_filenames:
        file_to_delete = filename.replace('/static/uploads/', '')
        file_path = os.path.join(UPLOADS_DIR, file_to_delete)
        if os.path.exists(file_path):
            os.remove(file_path)

    deleted_painting = await crud.painting.remove(db=db, id=painting_id)
    return deleted_painting