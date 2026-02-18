from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.database import get_db
from app.auth.utils import verify_token
from app.auth.exceptions import InvalidTokenException
from app.crud import user as user_crud
from app.schemas import TokenData

security = HTTPBearer()

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = verify_token(token)

        if payload.get("type") != "access":
            raise InvalidTokenException()

        user_id: str = payload.get("sub")  # !!! узнать почему str
        if user_id is None:
            raise InvalidTokenException()

        token_data = TokenData(user_id=user_id)

        user = await user_crud.get_user_by_id(db, user_id=int(token_data.user_id))
        if user is None:
            raise InvalidTokenException()
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь не активен"
            )
        return user
    except JWTError:
        raise InvalidTokenException()

async def get_current_active_user(current_user = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не активен"
        )
    return current_user

async def get_token_data(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    token = credentials.credentials
    payload = verify_token(token)
    return payload









































