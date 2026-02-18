from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings
from typing import AsyncGenerator

engine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=0,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Сохранять объекты после коммита
    autocommit=False,        # Ручное управление транзакциями
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

