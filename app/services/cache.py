import logging
import redis.asyncio as redis

logger = logging.getLogger(__name__)


def _cache_key(short_code: str) -> str:
    return f"url:{short_code}"


async def get_cached_url(client: redis.Redis, short_code: str) -> str | None:
    try:
        return await client.get(_cache_key(short_code))
    except Exception as e:
        logger.warning(f"Redis connection failed on get_cached_url: {e}")
        return None


async def set_cached_url(
    client: redis.Redis,
    short_code: str,
    long_url: str,
    ttl: int,
) -> None:
    try:
        await client.set(_cache_key(short_code), long_url, ex=ttl)
    except Exception as e:
        logger.warning(f"Redis connection failed on set_cached_url: {e}")


async def invalidate_cached_url(client: redis.Redis, short_code: str) -> None:
    try:
        await client.delete(_cache_key(short_code))
    except Exception as e:
        logger.warning(f"Redis connection failed on invalidate_cached_url: {e}")

