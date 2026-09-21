from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine(database_url: str) -> AsyncEngine:
    """Create SQLAlchemy async engine for the database."""

    return create_async_engine(database_url)


def create_session_factory(
        engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create factory for asynchronous database sessions."""

    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )
