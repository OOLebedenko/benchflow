from collections.abc import AsyncIterator
from typing import cast

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def get_session(
        request: Request,
) -> AsyncIterator[AsyncSession]:
    """Provide one database session for the current request."""

    session_factory = cast(
        async_sessionmaker[AsyncSession],
        request.app.state.session_factory,
    )

    # One AsyncSession lives for the duration of the dependency usage.
    # Closing it releases any checked-out connection back to the pool.
    async with session_factory() as session:
        yield session
