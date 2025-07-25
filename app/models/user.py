from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base

class User(Base):
    # Имя таблицы будет 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_superuser = Column(Boolean(), default=False)