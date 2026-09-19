from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyFlusher:
    """Flush pending changes with SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def flush(self) -> None:
        """Flush pending changes."""

        await self._session.flush()
