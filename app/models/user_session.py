from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserSession(Base):
    # SQLAlchemy автоматически назовет таблицу 'usersessions'
    id = Column(Integer, primary_key=True, index=True)

    # Время, когда была создана сессия (пользователь зашел на сайт)
    # БД сама установит текущее время при создании записи.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связь "один-к-одному" с таблицей Feedback.
    # Одна сессия может иметь только один отзыв.
    # `uselist=False` указывает на это.
    # `cascade` означает, что если мы удалим сессию, удалится и связанный отзыв.
    feedback = relationship(
        "Feedback",
        back_populates="user_session",
        uselist=False,  # <-- Ключевой момент для связи "один-к-одному"
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<UserSession(id={self.id}, created_at='{self.created_at}')>"