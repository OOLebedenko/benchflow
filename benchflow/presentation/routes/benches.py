from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from benchflow.application.services.benches import (
    BenchNotFoundError,
    BenchService,
)
from benchflow.presentation.dependencies.benches import (
    get_bench_service,
)
from benchflow.presentation.schemas.benches import BenchResponse

router = APIRouter(
    prefix="/benches",
    tags=["benches"],
)


@router.get(
    "",
    response_model=list[BenchResponse],
)
async def list_benches(
        bench_service: Annotated[
            BenchService,
            Depends(get_bench_service),
        ],
) -> list[BenchResponse]:
    """Return all benches."""

    benches = await bench_service.list_benches()

    return [
        BenchResponse(
            id=bench.id,
            name=bench.name,
            status=bench.status,
        )
        for bench in benches
    ]


@router.get(
    "/{bench_id}",
    response_model=BenchResponse,
)
async def get_bench(
        bench_id: UUID,
        bench_service: Annotated[
            BenchService,
            Depends(get_bench_service),
        ],
) -> BenchResponse:
    """Return a bench by its identifier."""

    try:
        bench = await bench_service.get_bench(bench_id)
    except BenchNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bench not found",
        ) from error

    return BenchResponse(
        id=bench.id,
        name=bench.name,
        status=bench.status,
    )
