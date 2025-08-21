import os
import json
from typing import Optional, Any
import redis.asyncio as redis
from loguru import logger

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
_client: redis.Redis | None = None

def get_client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(REDIS_URL, decode_responses=True)
    return _client

async def cache_get(key: str) -> Optional[Any]:
    try:
        val = await get_client().get(key)
        if val:
            return json.loads(val)
    except Exception as e:
        logger.warning(f"Cache get failed {key}: {e}")
    return None

async def cache_set(key: str, value: Any, ttl: int = 300):
    try:
        await get_client().set(key, json.dumps(value), ex=ttl)
    except Exception as e:
        logger.warning(f"Cache set failed {key}: {e}")
