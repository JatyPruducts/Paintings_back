from datetime import datetime
from pydantic import BaseModel, ConfigDict

# ------------------- Схемы для Сессии Пользователя -------------------

# Базовая схема. Клиент не передает никаких данных для создания сессии.
class UserSessionBase(BaseModel):
    pass


# Схема для создания записи о сессии.
class UserSessionCreate(UserSessionBase):
    pass


# Схема для чтения данных о сессии из БД.
class UserSessionInDB(UserSessionBase):
    id: int
    created_at: datetime

    # Разрешаем Pydantic работать с моделями SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)