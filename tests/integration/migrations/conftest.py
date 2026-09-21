import pytest
from alembic.config import Config

from tests.config import (
    create_alembic_config,
    create_test_database_url,
)

MIGRATION_DATABASE_NAME = "benchflow_migrations"


@pytest.fixture(scope="session")
def migration_database_url(
        database_url: str,
) -> str:
    """Provide an isolated PostgreSQL database for migration tests."""

    return create_test_database_url(
        database_url,
        MIGRATION_DATABASE_NAME,
    )


@pytest.fixture
def alembic_config(
        migration_database_url: str,
) -> Config:
    """Provide Alembic configuration for migration tests."""

    config = create_alembic_config()

    # Migration stairway tests may freely upgrade and downgrade
    # without changing the schema used by other integration tests.
    config.attributes["database_url"] = migration_database_url

    return config
