from typing import Any


def create_redis_client(url: str) -> Any:
    """Create an async Redis client for cache or coordination adapters."""
    from redis.asyncio import Redis

    return Redis.from_url(url, decode_responses=True)

