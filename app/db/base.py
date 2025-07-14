from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    """
    Базовый класс для всех моделей SQLAlchemy.
    Автоматически задает имя таблицы (__tablename__)
    в нижнем регистре на основе имени класса.
    """
    id: int
    __name__: str

    # Генерируем __tablename__ автоматически
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s" # Например, Painting -> paintings