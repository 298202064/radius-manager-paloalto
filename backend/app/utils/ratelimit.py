import time
import logging
from collections.abc import Callable
from typing import Optional

from fastapi import Request, HTTPException, status

from app.core.redis import get_redis

logger = logging.getLogger(__name__)


class RateLimitExceeded(HTTPException):
    def __init__(self, retry_after: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"请求过于频繁，请 {retry_after} 秒后再试",
            headers={"Retry-After": str(retry_after)},
        )


class RateLimiter:
    """Sliding-window rate limiter backed by Redis."""

    def __init__(
        self,
        route: str,
        max_requests: int,
        window_seconds: int,
        key_builder: Optional[Callable[[Request], str]] = None,
    ):
        self.route = route
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.key_builder = key_builder or self._default_key

    @staticmethod
    def _default_key(request: Request) -> str:
        client_ip = request.client.host if request.client else "unknown"
        # Honour reverse-proxy headers
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            client_ip = real_ip
        return client_ip

    async def __call__(self, request: Request) -> None:
        try:
            redis = await get_redis()
        except Exception as e:
            logger.warning("Redis unavailable, skipping rate limit: %s", e)
            return

        identifier = self.key_builder(request)
        key = f"ratelimit:{self.route}:{identifier}"

        now = time.time()
        window_start = now - self.window_seconds

        # Remove stale entries, count remaining, add current
        async with redis.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.expire(key, self.window_seconds)
            pipe.zadd(key, {str(now): now})
            _, count, _, _ = await pipe.execute()

        if count > self.max_requests:
            raise RateLimitExceeded(self.window_seconds)
