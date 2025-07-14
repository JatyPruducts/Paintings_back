from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.schemas.feedback import FeedbackInDB, FeedbackBase, FeedbackCreate
from app.schemas.user_session import UserSessionCreate
from app.api import deps

router = APIRouter()


@router.post("/", response_model=FeedbackInDB)
async def create_feedback(
        *,
        db: AsyncSession = Depends(deps.get_db),
        # Клиент отправляет только базовые данные отзыва
        feedback_in: FeedbackBase
):
    """
    Принять данные обратной связи от пользователя.
    При этом автоматически создается запись о сессии.
    """
    # 1. Создаем новую сессию для этого пользователя
    session_create_obj = UserSessionCreate()
    new_session = await crud.user_session.create(db=db, obj_in=session_create_obj)

    # 2. Создаем объект отзыва, добавляя в него ID только что созданной сессии
    feedback_create_obj = FeedbackCreate(
        **feedback_in.dict(),
        user_session_id=new_session.id
    )

    # 3. Сохраняем отзыв в базе данных
    new_feedback = await crud.feedback.create(db=db, obj_in=feedback_create_obj)

    return new_feedback