from app.crud.base import CRUDBase
from app.models.painting import Painting
from app.schemas.painting import PaintingCreate, PaintingUpdate

# Создаем класс для картин, наследуясь от базового
class CRUDPainting(CRUDBase[Painting, PaintingCreate, PaintingUpdate]):
    # Здесь можно добавлять специфичные для картин методы,
    # например, поиск по названию. Пока оставим пустым.
    pass

# Создаем единый экземпляр класса для использования во всем приложении
painting = CRUDPainting(Painting)