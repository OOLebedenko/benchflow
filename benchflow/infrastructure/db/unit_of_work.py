from collections.abc import Awaitable, Callable

from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from benchflow.application.ports.unit_of_work import (
    UniqueConstraintViolationError,
)
from benchflow.infrastructure.db.models.base import Base


class SqlAlchemyUnitOfWork:
    """Manage a transactional unit of work with SQLAlchemy."""

    def __init__(
            self,
            session: AsyncSession,
    ) -> None:
        self._session = session
        self._pending_deletes: list[Base] = []

    def stage_delete(
            self,
            model: Base,
    ) -> None:
        """Stage a persistence model for deletion."""

        self._pending_deletes.append(model)

    async def flush(self) -> None:
        """Synchronize pending changes with the database."""

        await self._execute(self._session.flush)

    async def commit(self) -> None:
        """Commit the current unit of work."""

        await self._execute(self._session.commit)

    async def rollback(self) -> None:
        """Roll back the current unit of work."""

        self._pending_deletes.clear()
        await self._session.rollback()

    async def _execute(
            self,
            operation: Callable[[], Awaitable[None]],
    ) -> None:
        """Execute a unit-of-work operation with rollback on failure."""

        try:
            await self._apply_pending_deletes()
            await operation()
        except IntegrityError as error:
            await self._rollback_after_failure(error)
            self._translate_integrity_error(error)
        except Exception as error:
            await self._rollback_after_failure(error)
            raise

    async def _rollback_after_failure(
            self,
            error: Exception,
    ) -> None:
        """Roll back while preserving the original failure."""

        try:
            await self.rollback()
        except Exception as rollback_error:
            raise rollback_error from error

    async def _apply_pending_deletes(self) -> None:
        """Register staged deletions with SQLAlchemy."""

        pending_deletes = self._pending_deletes
        self._pending_deletes = []

        for model in pending_deletes:
            await self._session.delete(model)

    @staticmethod
    def _translate_integrity_error(
            error: IntegrityError,
    ) -> None:
        """Translate known persistence constraint violations."""

        if isinstance(error.orig, UniqueViolation):
            raise UniqueConstraintViolationError from error

        raise error
