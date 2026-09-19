from collections.abc import AsyncIterator

import pytest
from alembic.command import upgrade
from psycopg import connect, sql
from sqlalchemy import delete
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from benchflow.infrastructure.db.models.user import UserModel
from benchflow.infrastructure.db.session import (
    create_engine,
    create_session_factory,
)
from tests.config import create_alembic_config

REPOSITORY_DATABASE_NAME = "benchflow_repositories"


@pytest.fixture(scope="session")
def repository_database_url(
        database_url: str,
) -> str:
    """Provide an isolated PostgreSQL database for repository tests."""

    # database_url points to the PostgreSQL instance created by the root
    # Testcontainers fixture. Reuse the same server, but create a separate
    # database so repository tests do not share schema state with other tests.
    base_url = make_url(database_url)

    # CREATE DATABASE must be executed outside a transaction.
    # Connect to the built-in postgres database only for this administrative
    # operation.
    admin_url = base_url.set(
        drivername="postgresql",
        database="postgres",
    )

    with connect(
            admin_url.render_as_string(hide_password=False),
            autocommit=True,
    ) as connection:
        connection.execute(
            sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(REPOSITORY_DATABASE_NAME)
            )
        )

    # Keep the original SQLAlchemy driver in the URL used by the application
    # and Alembic, changing only the database name.
    return base_url.set(
        database=REPOSITORY_DATABASE_NAME
    ).render_as_string(
        hide_password=False
    )


@pytest.fixture(scope="session")
def migrated_database_url(
        repository_database_url: str,
) -> str:
    """Provide repository database migrated to the latest revision."""

    config = create_alembic_config()

    # Apply the real application migrations to the isolated repository
    # database once before repository integration tests start.
    config.attributes["database_url"] = repository_database_url
    upgrade(config, "head")

    return repository_database_url


@pytest.fixture
async def session_factory(
        migrated_database_url: str,
) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    """Provide an async session factory for repository tests."""

    # Use the same async SQLAlchemy infrastructure as the application,
    # but connect it to the isolated repository test database.
    engine = create_engine(migrated_database_url)
    factory = create_session_factory(engine)

    try:
        # Return the factory rather than a single session because some tests
        # need several independent sessions and transactions.
        yield factory
    finally:
        # Tests may commit data, so clean persisted rows between tests while
        # leaving the migrated schema intact.
        async with factory() as session:
            await session.execute(delete(UserModel))
            await session.commit()

        # Release connections owned by this test's engine.
        await engine.dispose()
