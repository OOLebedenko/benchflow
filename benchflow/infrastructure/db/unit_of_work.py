from collections.abc import Awaitable, Callable
from typing import Any, NoReturn

from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from benchflow.application.ports.unit_of_work import (
    UniqueConstraintViolationError,
)
from benchflow.infrastructure.db.models.base import Base

type PendingUpdate = tuple[
    type[Base],
    Any,
    Callable[[Any], None],
]

type PendingDelete = tuple[
    type[Base],
    Any,
]


class SqlAlchemyUnitOfWork:
    """Manage a transactional unit of work with SQLAlchemy."""

    def __init__(
            self,
            session: AsyncSession,
    ) -> None:
        self._session = session
        self._pending_adds: list[Base] = []
        self._pending_updates: list[PendingUpdate] = []
        self._pending_deletes: list[PendingDelete] = []

    def stage_add(
            self,
            model: Base,
    ) -> None:
        """Stage a persistence model for addition."""

        self._pending_adds.append(model)

    def stage_update(
            self,
            model_type: type[Base],
            model_id: Any,
            apply: Callable[[Any], None],
    ) -> None:
        """Stage a persistence update to apply on flush."""

        self._pending_updates.append(
            (model_type, model_id, apply)
        )

    def stage_delete(
            self,
            model_type: type[Base],
            model_id: Any,
    ) -> None:
        """Stage a persistence model for deletion."""

        self._pending_deletes.append(
            (model_type, model_id)
        )

    async def flush(self) -> None:
        """Synchronize pending changes with the database."""

        await self._execute(self._session.flush)

    async def commit(self) -> None:
        """Commit the current unit of work."""

        await self._execute(self._session.commit)

    async def rollback(self) -> None:
        """Roll back the current unit of work."""

        self._pending_adds.clear()
        self._pending_updates.clear()
        self._pending_deletes.clear()

        await self._session.rollback()

    async def _execute(
            self,
            operation: Callable[[], Awaitable[None]],
    ) -> None:
        """Execute a unit-of-work operation with rollback on failure."""

        try:
            self._apply_pending_adds()
            await self._apply_pending_updates()
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

    def _apply_pending_adds(self) -> None:
        """Register staged additions with SQLAlchemy."""

        pending_adds = self._pending_adds
        self._pending_adds = []

        self._session.add_all(pending_adds)

    async def _apply_pending_updates(self) -> None:
        """Apply staged updates to persistence models."""

        pending_updates = self._pending_updates
        self._pending_updates = []

        for model_type, model_id, apply in pending_updates:
            model = await self._session.get(
                model_type,
                model_id,
            )

            if model is None:
                raise RuntimeError(
                    f"{model_type.__name__} {model_id} not found"
                )

            apply(model)

    async def _apply_pending_deletes(self) -> None:
        """Apply staged deletions to persistence models."""

        pending_deletes = self._pending_deletes
        self._pending_deletes = []

        for model_type, model_id in pending_deletes:
            model = await self._session.get(
                model_type,
                model_id,
            )

            if model is None:
                raise RuntimeError(
                    f"{model_type.__name__} {model_id} not found"
                )

            await self._session.delete(model)

    @staticmethod
    def _translate_integrity_error(
            error: IntegrityError,
    ) -> NoReturn:
        """Translate known persistence constraint violations."""

        if isinstance(error.orig, UniqueViolation):
            raise UniqueConstraintViolationError from error

        raise error
