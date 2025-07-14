from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.security import create_access_token
from app.crud import user as crud_user
from app.schemas.auth import Token

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Аутентифицирует пользователя и возвращает JWT токен.
    """
    # crud_user.authenticate должен быть асинхронным
    user = await crud_user.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}