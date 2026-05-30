import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT standard claims
JWT_ISSUER = "radius-manager"
JWT_AUDIENCE = "radius-api"

# Prefix for blacklisted token JTIs in Redis
_BLACKLIST_PREFIX = "token:blacklist:"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({
        "exp": expire,
        "type": "access",
        "jti": secrets.token_hex(16),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": datetime.now(timezone.utc),
    })
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "jti": secrets.token_hex(16),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": datetime.now(timezone.utc),
    })
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


async def revoke_token(jti: str, expires_at: datetime) -> None:
    """Add a token JTI to the Redis blacklist.

    The entry lives in Redis until the token's natural expiry so the
    blacklist is self-cleaning.
    """
    try:
        from app.core.redis import get_redis
        redis = await get_redis()
        ttl = int((expires_at - datetime.now(timezone.utc)).total_seconds())
        if ttl > 0:
            await redis.set(f"{_BLACKLIST_PREFIX}{jti}", "1", ex=ttl)
    except Exception:
        pass  # Blacklist is advisory — don't break the request


async def is_token_revoked(jti: str) -> bool:
    """Check whether a JTI has been blacklisted."""
    try:
        from app.core.redis import get_redis
        redis = await get_redis()
        return await redis.exists(f"{_BLACKLIST_PREFIX}{jti}") > 0
    except Exception:
        return False


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token.

    New tokens include ``iss`` and ``aud`` claims; old tokens issued before
    the upgrade lack them.  We check them when present for forward
    compatibility without breaking existing sessions.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={
                "verify_aud": False,   # checked manually for backward compat
                "verify_iss": False,
            },
        )
        # Verify issuer when present (new-style tokens)
        iss = payload.get("iss")
        if iss is not None and iss != JWT_ISSUER:
            return None
        # Verify audience when present
        aud = payload.get("aud")
        if aud is not None and aud != JWT_AUDIENCE:
            return None
        return payload
    except JWTError:
        return None
