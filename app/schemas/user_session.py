from datetime import datetime
from pydantic import BaseModel, ConfigDict
from .painting import ArticleInDB

# ------------------- Схемы для Сессии Пользователя -------------------

# Базовая схема. Клиент не передает никаких данных для создания сессии.
class UserSessionBase(BaseModel):
    pass


# Схема для создания записи о сессии.
class UserSessionCreate(UserSessionBase):
    pass


# Схема для чтения данных о сессии из БД.
class UserSessionInDB(UserSessionBase, ArticleInDB):
    created_at: datetime