import os
from pydantic_settings import BaseSettings
from pydantic import model_validator

_WEAK_SECRETS = frozenset({
    "change-me-in-production",
    "your-super-secret-jwt-key-change-in-production",
    "radius-system-secret-key-change-in-production-2026",
})


class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://radius:radiuspass@postgres:5432/radius"
    )

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    # JWT
    secret_key: str = ""
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Encryption (Fernet)
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "")

    # CORS
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:8080")

    # Algorithm
    algorithm: str = "HS256"

    # RADIUS internal endpoint security
    radius_allowed_ips: str = os.getenv(
        "RADIUS_ALLOWED_IPS",
        "127.0.0.1,::1,172.16.0.0/12,10.0.0.0/8,192.168.0.0/16"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False

    @model_validator(mode="after")
    def validate_secret_key(self):
        if not self.secret_key or len(self.secret_key) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters. "
                "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )
        if self.secret_key in _WEAK_SECRETS:
            raise ValueError(
                f"SECRET_KEY is set to a known weak value. Please generate a strong random key."
            )
        return self


settings = Settings()
