from datetime import datetime
from pydantic import BaseModel, ConfigDict

# ------------------- Схемы для Обратной Связи -------------------

# Базовая схема с полями, которые пользователь отправляет с фронтенда.
class FeedbackBase(BaseModel):
    user_name: str
    phone_number: str
    painting_id: int # ID картины, к которой относится отзыв.


# Схема для создания записи в БД. Она включает в себя ID сессии,
# который мы определим и добавим на бэкенде.
class FeedbackCreate(FeedbackBase):
    user_session_id: int


# Схема для чтения данных об отзыве из БД.
class FeedbackInDB(FeedbackBase):
    id: int
    submitted_at: datetime
    user_session_id: int

    # Разрешаем Pydantic работать с моделями SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)