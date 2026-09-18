import pytest
from alembic.config import Config

from tests.config import create_alembic_config


@pytest.fixture
def alembic_config(database_url: str) -> Config:
    """Provide Alembic configuration for the test PostgreSQL database."""

    config = create_alembic_config()

    # Override the application database URL with the PostgreSQL instance
    # created by Testcontainers.
    config.attributes["database_url"] = database_url

    return config
