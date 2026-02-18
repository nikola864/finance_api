from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import user as user_crud
from app.schemas import UserCreate, LoginRequest, UserUpdate, UserResponse
from app.auth.utils import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from app.auth.exceptions import UserAlreadyExistsException, InvalidCredentialsException, UserNotFoundException, \
    InvalidTokenException


class AuthService:
    """Сервис для аутентификации и управления пользователями"""

    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate):

        # Шаг 1: Проверяем, существует ли пользователь с таким email
        existing_user = await user_crud.get_user_by_email(db, email=user_data.email)
        if existing_user:
            raise UserAlreadyExistsException()

        # Шаг 2: Хешируем пароль
        hashed_password = hash_password(user_data.password)

        # Шаг 3: Подготавливаем данные для создания пользователя
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]

        # Шаг 4: Создаем пользователя в базе
        new_user = await user_crud.create_user(db, user_dict)
        return UserResponse.model_validate(new_user)

    @staticmethod
    async def authenticate_user(db: AsyncSession, credentials: LoginRequest):

        # Шаг 1: Находим пользователя по email
        user = await user_crud.get_user_by_email(db, credentials.email)
        if not user:
            raise InvalidCredentialsException()

        # Шаг 2: Проверяем пароль
        if not verify_password(credentials.password, user.hashed_password):
            raise InvalidCredentialsException()

        # Шаг 3: Генерируем токены
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token: str):
        try:
            # Шаг 1: Декодируем refresh токен
            payload = verify_token(refresh_token)

            # Шаг 2: Проверяем тип токена
            if payload.get("type") != "refresh":
                raise InvalidTokenException()

            # Шаг 3: Извлекаем user_id
            user_id = payload.get("sub")
            if not user_id:
                raise InvalidTokenException()

            # Шаг 4: Находим пользователя в базе
            user = await user_crud.get_user_by_id(db, user_id=int(user_id))
            if not user:
                raise UserNotFoundException()

            # Шаг 5: Проверяем активность пользователя
            if not user.is_active:
                raise InvalidCredentialsException()

            # Шаг 6: Генерируем новый access токен
            new_access_token = create_access_token(data={"sub": str(user.id)})

            return {
                "access_token": new_access_token,
                "token_type": "bearer"
            }

        except Exception:
            raise InvalidTokenException()

    @staticmethod
    async def get_user_profile(db: AsyncSession, user_id: int):
        user = await user_crud.get_user_by_id(db, user_id=user_id)
        if not user:
            raise UserNotFoundException()
        return user

    @staticmethod
    async def update_user_profile(db: AsyncSession, user_id: int, update_data: UserUpdate):
        user = await user_crud.get_user_by_id(db, user_id=user_id)
        if not user:
            raise UserNotFoundException()

        updated_user = await user_crud.update_user(db, user_id=user_id, user_update=update_data)
        return updated_user

    @staticmethod
    async def delete_user_account(db: AsyncSession, user_id: int):
        user = await user_crud.get_user_by_id(db, user_id=user_id)
        if not user:
            raise UserNotFoundException()

        await user_crud.delete_user(db, user_id=user_id)
        return {"message": "Аккаунт успешно удален"}
























