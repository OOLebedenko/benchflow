from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from benchflow.application.ports.unit_of_work import UniqueConstraintViolationError


class SqlAlchemyFlusher:
    """Flush pending changes with SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def flush(self) -> None:
        """Flush pending changes."""

        try:
            await self._session.flush()
        except IntegrityError as error:
            # SQLAlchemy wraps the original PostgreSQL/psycopg exception.
            # Translate only UNIQUE violations
            if isinstance(error.orig, UniqueViolation):
                raise UniqueConstraintViolationError from error
            raise
