from redis.asyncio import Redis


async def test_redis_connection(
        redis_client: Redis,
) -> None:
    """Connect to the integration Redis instance."""

    assert await redis_client.ping() is True
