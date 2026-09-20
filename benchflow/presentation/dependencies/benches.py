from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from benchflow.application.services.benches import BenchService
from benchflow.infrastructure.repositories.bench import (
    SqlAlchemyBenchRepository,
)
from benchflow.presentation.dependencies.database import get_session


async def get_bench_service(
        session: Annotated[AsyncSession, Depends(get_session)],
) -> BenchService:
    """Provide bench service for the current request."""

    repository = SqlAlchemyBenchRepository(session)

    return BenchService(
        bench_repository=repository,
    )
