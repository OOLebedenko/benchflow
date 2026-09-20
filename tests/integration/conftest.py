from collections.abc import AsyncIterator

import pytest
from alembic.command import upgrade
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from benchflow.infrastructure.db.models.bench import BenchModel
from benchflow.infrastructure.db.models.user import UserModel
from benchflow.infrastructure.db.session import (
    create_engine,
    create_session_factory,
)
from tests.config import (
    create_alembic_config,
    create_test_database_url,
)

INTEGRATION_DATABASE_NAME = "benchflow_integration"


@pytest.fixture(scope="session")
def integration_database_url(
        database_url: str,
) -> str:
    """Provide an isolated PostgreSQL database for integration tests."""

    return create_test_database_url(
        database_url,
        INTEGRATION_DATABASE_NAME,
    )


@pytest.fixture(scope="session")
def migrated_database_url(
        integration_database_url: str,
) -> str:
    """Provide integration database migrated to the latest revision."""

    config = create_alembic_config()

    # Repository and API tests expect a stable production-like
    # schema at the latest migration revision.
    config.attributes["database_url"] = integration_database_url
    upgrade(config, "head")

    return integration_database_url


@pytest.fixture
async def session_factory(
        migrated_database_url: str,
) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    """Provide an async session factory for integration tests."""

    engine = create_engine(migrated_database_url)
    factory = create_session_factory(engine)

    try:
        # Tests receive the factory so they can create several
        # independent sessions and transactions when necessary.
        yield factory
    finally:
        # Integration tests may commit data, so clean persisted rows
        # before the next test while keeping the schema intact.
        async with factory() as session:
            await session.execute(delete(BenchModel))
            await session.execute(delete(UserModel))
            await session.commit()

        await engine.dispose()
