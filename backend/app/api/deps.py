import aioredis

# Create a global Redis pool
redis_pool = None

async def init_redis():
    global redis_pool
    redis_pool = await aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        max_connections=100,  # Increase for better concurrency
        socket_keepalive=True,  # Reduce reconnections
        socket_timeout=5,  # Prevent long blocking calls
        encoding="utf-8",
        decode_responses=True
    )

async def get_redis_client() -> aioredis.Redis:
    """Use the global Redis connection to avoid re-initialization latency."""
    return redis_pool

# ... existing code ...