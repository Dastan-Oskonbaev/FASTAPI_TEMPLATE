from arq.connections import RedisSettings, create_pool

from src.core.config import settings


redis_settings = RedisSettings(settings.REDIS_HOST, settings.REDIS_PORT)

async def get_redis_pool():
    return await create_pool(redis_settings)

async def init_redis_pool(app):
    app.state.redis = await create_pool(redis_settings)

async def close_redis_pool(app):
    redis = getattr(app.state, "redis", None)
    if redis:
        await redis.close()