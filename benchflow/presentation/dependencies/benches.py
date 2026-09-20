from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from benchflow.application.services.benches import BenchService
from benchflow.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from benchflow.infrastructure.repositories.bench import (
    SqlAlchemyBenchRepository,
)
from benchflow.presentation.dependencies.database import get_session


async def get_bench_service(
        session: Annotated[
            AsyncSession,
            Depends(get_session),
        ],
) -> BenchService:
    """Provide bench service for the current request."""

    unit_of_work = SqlAlchemyUnitOfWork(session)
    repository = SqlAlchemyBenchRepository(
        session,
        unit_of_work,
    )

    return BenchService(
        bench_repository=repository,
        unit_of_work=unit_of_work,
    )
