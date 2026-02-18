from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import UserCreate, LoginRequest, Token, UserResponse, UserUpdate
from app.auth.dependencies import get_current_user
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await AuthService.register_user(db, user_data)
    return user

@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, db:AsyncSession = Depends(get_db)):
    result = await AuthService.authenticate_user(db, credentials)

    return Token(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        token_type="bearer"
    )

@router.post("/refresh", response_model=Token)
async def refreshed_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    result = await AuthService.refresh_access_token(db, refresh_token)
    return Token(
        access_token=result["access_token"],
        token_type="bearer"
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user(
        update_data: UserUpdate,
        current_user = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    updated_user = await AuthService.update_user_profile(db, user_id=current_user.id, update_data=update_data)
    return updated_user

@router.delete("/me")
async def delete_account(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await AuthService.delete_user_account(db, user_id=current_user.id)
    return {"message": "Аккаунт успешно удален"}
