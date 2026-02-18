from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    DEBUG: bool = False

    # JWT settings
    SECRET_KEY: str = ""  # Обязательно измените в .env!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React/Vue/Angular dev server
        "http://localhost:8000",  # FastAPI docs
        "http://localhost:5173",  # Vite dev server
    ]

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False, # Игнорировать регистр переменных
        extra="forbid"        # Запретить необъявленные переменные
    )

settings = Settings()
