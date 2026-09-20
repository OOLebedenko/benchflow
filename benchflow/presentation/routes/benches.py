from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from benchflow.application.services.benches import (
    BenchNotFoundError,
    BenchService,
)
from benchflow.domain.bench import Bench
from benchflow.presentation.dependencies.benches import get_bench_service
from benchflow.presentation.schemas.benches import (
    BenchCreateRequest,
    BenchResponse,
    BenchUpdateRequest,
)

router = APIRouter(
    prefix="/benches",
    tags=["benches"],
)


def _to_response(
        bench: Bench,
) -> BenchResponse:
    """Convert a domain bench to an HTTP response."""

    return BenchResponse(
        id=bench.id,
        name=bench.name,
        status=bench.status,
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
        _to_response(bench)
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

    return _to_response(bench)


@router.post(
    "",
    response_model=BenchResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_bench(
        data: BenchCreateRequest,
        bench_service: Annotated[
            BenchService,
            Depends(get_bench_service),
        ],
) -> BenchResponse:
    """Create a bench."""

    bench = await bench_service.create_bench(
        name=data.name,
        status=data.status,
    )

    return _to_response(bench)


@router.patch(
    "/{bench_id}",
    response_model=BenchResponse,
)
async def update_bench(
        bench_id: UUID,
        data: BenchUpdateRequest,
        bench_service: Annotated[
            BenchService,
            Depends(get_bench_service),
        ],
) -> BenchResponse:
    """Update a bench."""

    try:
        bench = await bench_service.update_bench(
            bench_id=bench_id,
            name=data.name,
            status=data.status,
        )
    except BenchNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bench not found",
        ) from error

    return _to_response(bench)
