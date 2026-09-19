from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyTransactionManager:
    """Manage transactions with SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        """Commit the current transaction."""

        await self._session.commit()
