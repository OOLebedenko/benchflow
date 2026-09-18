from collections.abc import Generator

import pytest
from testcontainers.community.postgres import PostgresContainer

from tests.config import POSTGRES_DRIVER, POSTGRES_IMAGE


@pytest.fixture(scope="session")
def database_url() -> Generator[str, None, None]:
    """Provide PostgreSQL connection URL for integration tests."""

    with PostgresContainer(
            POSTGRES_IMAGE,
            driver=POSTGRES_DRIVER,
    ) as postgres:
        yield postgres.get_connection_url()
