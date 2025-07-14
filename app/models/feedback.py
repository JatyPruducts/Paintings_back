from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Feedback(Base):
    id = Column(Integer, primary_key=True, index=True)

    user_name = Column(String(255), nullable=False)
    phone_number = Column(String(50), nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- Связи с другими таблицами ---

    # 1. Связь с картиной (многие-к-одному: много отзывов могут относиться к одной картине)
    painting_id = Column(Integer, ForeignKey("paintings.id"), nullable=False)
    painting = relationship("Painting", back_populates="feedbacks")

    # 2. Связь с сессией (один-к-одному: один отзыв относится ровно к одной сессии)
    # ForeignKey указывает на 'usersessions.id'.
    # `unique=True` гарантирует, что на одну сессию не может быть двух отзывов.
    user_session_id = Column(Integer, ForeignKey("usersessions.id"), unique=True, nullable=False)
    user_session = relationship("UserSession", back_populates="feedback")

    def __repr__(self):
        return f"<Feedback(user='{self.user_name}', painting_id={self.painting_id})>"