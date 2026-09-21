from uuid import UUID

from pydantic import BaseModel

from benchflow.domain.run import RunStatus


class RunResponse(BaseModel):
    """Represent a run in API responses."""

    id: UUID
    bench_id: UUID
    status: RunStatus
