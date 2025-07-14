from app.crud.base import CRUDBase
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate
from pydantic import BaseModel

# У нас нет схемы для обновления отзыва, поэтому можно использовать BaseModel
class CRUDFeedback(CRUDBase[Feedback, FeedbackCreate, BaseModel]):
    pass

feedback = CRUDFeedback(Feedback)