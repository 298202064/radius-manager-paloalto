import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User
from app.models.refresh_token import RefreshToken


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(self, username: str, password: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if user is None or not user.enabled:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    async def create_tokens(self, user: User) -> dict:
        access_token = create_access_token({"sub": user.username})
        refresh_token_value = create_refresh_token({"sub": user.username})

        # Store refresh token hash
        token_hash = hashlib.sha256(refresh_token_value.encode()).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )

        self.db.add(RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        ))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token_value,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
            },
        }

    async def refresh_access_token(self, refresh_token_value: str) -> dict | None:
        payload = decode_token(refresh_token_value)
        if payload is None or payload.get("type") != "refresh":
            return None

        token_hash = hashlib.sha256(refresh_token_value.encode()).hexdigest()
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
        )
        stored = result.scalar_one_or_none()
        if stored is None:
            return None

        # Delete the used refresh token (rotation)
        await self.db.delete(stored)

        username = payload.get("sub")
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if user is None or not user.enabled:
            return None

        return await self.create_tokens(user)

    async def logout(self, refresh_token_value: str) -> None:
        token_hash = hashlib.sha256(refresh_token_value.encode()).hexdigest()
        await self.db.execute(
            delete(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
