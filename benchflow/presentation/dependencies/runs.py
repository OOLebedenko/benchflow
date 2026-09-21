from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from benchflow.application.ports.bench_lock import BenchLock
from benchflow.application.services.runs import RunService
from benchflow.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from benchflow.infrastructure.repositories.bench import (
    SqlAlchemyBenchRepository,
)
from benchflow.infrastructure.repositories.run import (
    SqlAlchemyRunRepository,
)
from benchflow.presentation.dependencies.database import get_session
from benchflow.presentation.dependencies.redis import get_bench_lock


async def get_run_service(
        session: Annotated[
            AsyncSession,
            Depends(get_session),
        ],
        bench_lock: Annotated[
            BenchLock,
            Depends(get_bench_lock),
        ],
) -> RunService:
    """Provide a run application service."""

    unit_of_work = SqlAlchemyUnitOfWork(session)

    bench_repository = SqlAlchemyBenchRepository(
        session,
        unit_of_work,
    )
    run_repository = SqlAlchemyRunRepository(
        unit_of_work,
    )

    return RunService(
        bench_repository=bench_repository,
        run_repository=run_repository,
        unit_of_work=unit_of_work,
        bench_lock=bench_lock,
    )
