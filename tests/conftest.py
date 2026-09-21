import asyncio
from collections.abc import AsyncIterator, Generator

import pytest
from redis.asyncio import Redis
from redis.exceptions import ConnectionError
from testcontainers.community.postgres import PostgresContainer
from testcontainers.core.container import DockerContainer

from benchflow.infrastructure.redis.client import create_redis
from tests.config import (
    POSTGRES_DRIVER,
    POSTGRES_IMAGE,
    REDIS_IMAGE,
    REDIS_PORT,
)


@pytest.fixture(scope="session")
def database_url() -> Generator[str, None, None]:
    """Provide PostgreSQL connection URL for integration tests."""

    with PostgresContainer(
            POSTGRES_IMAGE,
            driver=POSTGRES_DRIVER,
    ) as postgres:
        yield postgres.get_connection_url()


@pytest.fixture(scope="session")
def redis_url() -> Generator[str, None, None]:
    """Provide Redis connection URL for integration tests."""

    with (
            DockerContainer(REDIS_IMAGE)
                    .with_exposed_ports(REDIS_PORT)
    ) as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(REDIS_PORT)

        yield f"redis://{host}:{port}/0"


@pytest.fixture
async def redis_client(
        redis_url: str,
) -> AsyncIterator[Redis]:
    """Provide an async Redis client for integration tests."""

    client = create_redis(redis_url)

    # Docker may expose the port before Redis is ready to accept commands.
    for _ in range(50):
        try:
            await client.ping()
            break
        except ConnectionError:
            await asyncio.sleep(0.1)
    else:
        await client.aclose()
        raise RuntimeError("Redis test container did not become ready")

    try:
        await client.flushdb()
        yield client
    finally:
        await client.flushdb()
        await client.aclose()
