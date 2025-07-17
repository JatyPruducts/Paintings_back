from pydantic import BaseModel, ConfigDict, Field
from typing import List, Union


class ArticleInDB(BaseModel):
    # Поле называется 'article', но его значение будет браться из атрибута 'id'
    id: int = Field(serialization_alias='article_code')

    # Важно: конфигурация разрешает использовать псевдонимы при генерации ответа
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# ------------------- Схемы для Картины -------------------

# Базовая схема с общими полями, которые есть и при создании, и при чтении.
class PaintingBase(BaseModel):
    title: str
    width: float
    height: float
    tags: List[str]
    description: str
    photo_filenames: List[str]


# Схема для создания новой картины (что клиент отправляет на сервер).
class PaintingCreate(PaintingBase):
    pass


# Схема для обновления существующей картины.
# Все поля опциональны, т.к. клиент может захотеть обновить только часть данных.
class PaintingUpdate(BaseModel):
    title: Union[str, None] = None
    width: Union[float, None] = None
    height: Union[float, None] = None
    tags: Union[List[str], None] = None
    description: Union[str, None] = None
    photo_filenames: Union[List[str], None] = None


# Схема для чтения данных о картине из БД (что сервер отправляет клиенту).
# Наследуется от базовой схемы и добавляет поля, генерируемые сервером.
class PaintingInDB(PaintingBase, ArticleInDB):
    pass


class TotalPagesResponse(BaseModel):
    total_pages: int