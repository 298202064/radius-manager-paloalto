import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://radius:radiuspass@postgres:5432/radius"
    )

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Encryption (Fernet)
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "")

    # CORS
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:8080")

    # Algorithm
    algorithm: str = "HS256"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
