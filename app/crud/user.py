from pydantic import EmailStr
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas import UserCreate, UserUpdate
from app.auth.utils import hash_password

async def create_user(db: AsyncSession, user: dict) -> User:
    db_user = User(
        username=user["username"],
        email=user["email"],
        hashed_password=user["hashed_password"],
        is_active=True,
        is_superuser=False
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: EmailStr) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def update_user(
    db: AsyncSession,
    user_id: int,
    user_update: UserUpdate
) -> User | None:
    query = (
        update(User).where(User.id == user_id).values(**user_update.model_dump(exclude_unset=True)).returning(User)
    )
    result = await db.execute(query)
    await db.commit()
    return result.scalar_one_or_none()

async def delete_user(db: AsyncSession, user_id: int) -> bool:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return False
    await db.delete(user)
    await db.commit()
    return True


async def authenticate_user(
        db: AsyncSession,
        email: EmailStr,
        password: str,
        pwd_context
) -> User | None:
    user = await get_user_by_email(db, email)
    if not user:
        user = await db.execute(
            select(User).where(User.email == email)
        )
        user = user.scalar_one_or_none()

    if not user or not user.verify_password(password, pwd_context):
        return None
    return user




















