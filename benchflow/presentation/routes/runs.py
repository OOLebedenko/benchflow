from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from benchflow.application.services.benches import BenchNotFoundError
from benchflow.application.services.runs import (
    BenchUnavailableError,
    RunService,
)
from benchflow.presentation.dependencies.runs import get_run_service
from benchflow.presentation.schemas.runs import RunResponse

router = APIRouter(
    prefix="/benches",
    tags=["runs"],
)


@router.post(
    "/{bench_id}/runs",
    response_model=RunResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_run(
        bench_id: UUID,
        run_service: Annotated[
            RunService,
            Depends(get_run_service),
        ],
) -> RunResponse:
    """Start a run on an available bench."""

    try:
        run = await run_service.start_run(bench_id)
    except BenchNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bench not found",
        ) from error
    except BenchUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bench is not available",
        ) from error

    return RunResponse(
        id=run.id,
        bench_id=run.bench_id,
        status=run.status,
    )
