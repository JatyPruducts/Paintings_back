from sqlalchemy import Column, Integer, String, Numeric, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base


class Painting(Base):
    # Имя таблицы будет 'paintings' согласно правилу в Base
    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), index=True, nullable=False)
    width = Column(Numeric(10, 2), nullable=False)  # 10 знаков всего, 2 после запятой
    height = Column(Numeric(10, 2), nullable=False)

    # Используем специфичный для PostgreSQL тип ARRAY для хранения списков
    tags = Column(ARRAY(String), nullable=False)

    description = Column(Text, nullable=True)

    # Список имен файлов фотографий
    photo_filenames = Column(ARRAY(String), nullable=False)

    # Связь с таблицей Feedback
    # 'back_populates' создает двустороннюю связь.
    # 'cascade' означает, что при удалении картины удалятся и все связанные отзывы.
    feedbacks = relationship(
        "Feedback",
        back_populates="painting",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Painting(title='{self.title}')>"