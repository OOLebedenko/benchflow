from redis.asyncio import Redis


def create_redis(
        redis_url: str,
) -> Redis:
    """Create an asynchronous Redis client."""

    return Redis.from_url(
        redis_url,
        decode_responses=True,
    )
