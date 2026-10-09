import json

from redis.asyncio import Redis
from core.config import settings

redis_client = Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


async def get_cache(key: str):
    value = await redis_client.get(key)
    return json.loads(value) if value else None


async def set_cache(
    key: str,
    value: dict,
    expire_seconds: int = 60,
):
    await redis_client.set(
        key,
        json.dumps(value, default=str),
        ex=expire_seconds,
    )


async def delete_cache(key: str):
    await redis_client.delete(key)