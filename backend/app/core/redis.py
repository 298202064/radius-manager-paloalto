from redis.asyncio import Redis, ConnectionPool

from app.core.config import settings

_pool: ConnectionPool | None = None


async def get_redis() -> Redis:
    """Get or create the shared Redis async connection."""
    global _pool
    if _pool is None:
        _pool = ConnectionPool.from_url(
            settings.redis_url, max_connections=10, decode_responses=True
        )
    return Redis(connection_pool=_pool)


async def close_redis() -> None:
    """Disconnect the Redis pool (called on app shutdown)."""
    global _pool
    if _pool is not None:
        await _pool.disconnect()
        _pool = None
