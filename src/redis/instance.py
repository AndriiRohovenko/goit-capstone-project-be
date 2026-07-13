import redis.asyncio as redis
from redis.exceptions import RedisError
from src.conf.config import config
from typing import Any
import json

try:
    redis_client = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        password=config.REDIS_PASSWORD,
        decode_responses=True,
    )
except RedisError as e:
    print(f"❌ Redis connection error: {e}")


async def cache_get(key: str, client: redis.Redis) -> Any:
    value = await client.get(key)
    if value:
        return json.loads(value)
    return None


async def cache_set(key: str, value: Any, ttl: int, client: redis.Redis):
    await client.setex(key, ttl, json.dumps(value))
