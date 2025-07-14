from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.auth import TokenData
from app.crud import user as crud_user

# Эта строка создает "схему" аутентификации.
# tokenUrl указывает на эндпоинт, который выдает токен.
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/api/auth/login"
)


# АСИНХРОННАЯ зависимость для получения сессии БД.
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость для получения сессии БД."""
    async with SessionLocal() as session:
        yield session


async def get_current_user(
        db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    """
    Декодирует токен, проверяет его и возвращает пользователя из БД.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    # crud_user должен быть асинхронным
    user = await crud_user.get_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_superuser(
        current_user: User = Depends(get_current_user),
) -> User:
    """
    Проверяет, является ли пользователь, полученный из токена, суперюзером.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user